"""
메시지 핸들러 (Message Handler)

WebSocket 메시지를 처리하고 게임 상태를 업데이트합니다.
"""

import json
from typing import Dict, Optional
from app.models.game import Game
from app.game.game_manager import GameManager
from app.game.turn_manager import TurnManager
from app.game.action_handler import ActionHandler
from app.websocket.connection_manager import ConnectionManager
from app.utils.constants import ActionType, GameState, MIN_PLAYERS, MAX_PLAYERS


class MessageHandler:
    """
    메시지 핸들러 클래스
    
    WebSocket 메시지를 처리하고 게임 로직과 통신합니다.
    """
    
    def __init__(
        self,
        game_manager: GameManager,
        connection_manager: ConnectionManager,
    ):
        """
        메시지 핸들러 초기화
        
        Args:
            game_manager: GameManager 인스턴스
            connection_manager: ConnectionManager 인스턴스
        """
        self.game_manager = game_manager
        self.connection_manager = connection_manager

    def _error(self, message: str, code: str = "BAD_REQUEST") -> Dict:
        """
        표준화된 에러 응답을 생성합니다.

        Args:
            message: 에러 메시지
            code: 에러 코드 (클라이언트에서 분기 처리용)

        Returns:
            에러 응답 딕셔너리
        """
        return {
            "success": False,
            "message": message,
            "error_code": code,
        }
    
    async def handle_message(self, player_id: str, message: dict) -> Dict:
        """
        플레이어로부터 받은 메시지를 처리합니다.
        
        Args:
            player_id: 플레이어 ID
            message: 받은 메시지
            
        Returns:
            처리 결과
        """
        try:
            message_type = message.get("type")
            
            if message_type == "PLAYER_ACTION":
                return await self.handle_player_action(player_id, message)
            elif message_type == "JOIN_GAME":
                return await self.handle_join_game(player_id, message)
            elif message_type == "GET_GAME_STATE":
                return await self.handle_get_game_state(player_id, message)
            elif message_type == "START_GAME":
                return await self.handle_start_game(player_id, message)
            elif message_type == "ADD_AI_PLAYER":
                return await self.handle_add_ai_player(player_id, message)
            else:
                return self._error(
                    message=f"지원하지 않는 메시지 타입: {message_type}",
                    code="UNSUPPORTED_MESSAGE_TYPE",
                )
        except Exception as e:
            # 예외 발생 시 에러 메시지 반환
            import traceback
            print(f"[ERROR] handle_message 예외 발생: {type(e).__name__}: {e}")
            traceback.print_exc()
            return self._error(
                message="메시지 처리 중 서버 내부 오류가 발생했습니다.",
                code="INTERNAL_ERROR",
            )
    
    async def handle_player_action(self, player_id: str, message: dict) -> Dict:
        """
        플레이어 액션 메시지를 처리합니다.
        
        Args:
            player_id: 플레이어 ID
            message: {
                "type": "PLAYER_ACTION",
                "action": {
                    "type": "USE_CARD" | "RESPOND_ATTACK" | "END_TURN",
                    "cardId": "string (optional, USE_CARD 시 필수)",
                    "targetId": "string (optional, USE_CARD 시 타겟 필요 시 필수)",
                    "response": "evade" | "give_up" (RESPOND_ATTACK 시 필수)
                }
            }
            
        Returns:
            처리 결과
        """
        game_id = self.connection_manager.get_player_game(player_id)
        if not game_id:
            return self._error(
                message="플레이어가 게임에 참여하지 않았습니다.",
                code="PLAYER_NOT_IN_GAME",
            )
        
        game = self.game_manager.get_game(game_id)
        if not game:
            return self._error(
                message="게임을 찾을 수 없습니다.",
                code="GAME_NOT_FOUND",
            )
        
        # 게임 로직 컴포넌트 생성
        from app.game.card_manager import CardManager
        from app.game.turn_manager import TurnManager
        from app.game.action_handler import ActionHandler
        
        card_manager = self.game_manager.get_card_manager(game_id)
        turn_manager = TurnManager(game, card_manager)
        action_handler = ActionHandler(game, turn_manager, card_manager)
        
        # 새로운 메시지 형식 파싱
        action = message.get("action", {})
        if not action:
            return self._error(
                message="액션 정보가 필요합니다.",
                code="ACTION_REQUIRED",
            )
        
        action_type_str = action.get("type")
        try:
            action_type = ActionType(action_type_str)
        except ValueError:
            return self._error(
                message=f"잘못된 액션 타입: {action_type_str}",
                code="INVALID_ACTION_TYPE",
            )
        
        # 액션 타입별 데이터 변환 (기존 ActionHandler 형식으로)
        if action_type == ActionType.USE_CARD:
            data = {
                "card_id": action.get("cardId"),
                "target_id": action.get("targetId"),
            }
            result = action_handler.handle_action(action_type, player_id, data)
        elif action_type == ActionType.RESPOND_ATTACK:
            response = action.get("response")
            if response == "evade":
                # 회피 카드 사용 - cardId 필요
                data = {
                    "card_id": action.get("cardId"),
                }
                result = action_handler.handle_action(action_type, player_id, data)
            elif response == "give_up":
                # 포기 - handle_respond_attack_failed 호출
                result = action_handler.handle_respond_attack_failed(player_id)
            else:
                return self._error(
                    message=f"잘못된 응답 타입: {response}",
                    code="INVALID_RESPONSE_TYPE",
                )
        elif action_type == ActionType.END_TURN:
            data = {}
            result = action_handler.handle_action(action_type, player_id, data)
        elif action_type == ActionType.USE_TREASURE:
            data = {
                "treasure": action.get("treasure"),
                "card_ids": action.get("cardIds") or [],
            }
            result = action_handler.handle_action(action_type, player_id, data)
        elif action_type == ActionType.SELECT_STEAL_CARD:
            data = {
                "card_id": action.get("cardId"),
            }
            result = action_handler.handle_action(action_type, player_id, data)
        elif action_type == ActionType.SELECT_DRAW_ORDER:
            data = {
                "take_card_id": action.get("takeCardId"),
                "top_card_id": action.get("topCardId"),
                "bottom_card_id": action.get("bottomCardId"),
            }
            result = action_handler.handle_action(action_type, player_id, data)
        elif action_type == ActionType.GENERAL_STORE_PICK:
            data = {
                "card_id": action.get("cardId"),
            }
            result = action_handler.handle_action(action_type, player_id, data)
        else:
            return self._error(
                message=f"지원하지 않는 액션 타입: {action_type_str}",
                code="UNSUPPORTED_ACTION_TYPE",
            )
        
        # 게임 상태 업데이트 전송
        if result.get("success"):
            await self.broadcast_game_state(game_id)
        
        # 승리 조건 체크
        win_info = self.game_manager.check_win_condition(game_id)
        if win_info:
            await self.broadcast_game_state(game_id)
            await self.broadcast_win_info(game_id, win_info)
        
        return result
    
    async def handle_join_game(self, player_id: str, message: dict) -> Dict:
        """
        게임 참여 메시지를 처리합니다.
        
        Args:
            player_id: 플레이어 ID
            message: {
                "type": "JOIN_GAME",
                "game_id": str,
                "player_name": str
            }
            
        Returns:
            처리 결과
        """
        game_id = message.get("game_id")
        player_name = message.get("player_name", f"Player_{player_id}")
        
        if not game_id:
            return self._error(
                message="게임 ID가 필요합니다.",
                code="GAME_ID_REQUIRED",
            )
        
        # 게임 조회 또는 생성
        game = self.game_manager.get_game(game_id)
        if not game:
            game = self.game_manager.create_game(game_id)
        
        # 플레이어 추가
        success = self.game_manager.add_player_to_game(
            game_id, player_id, player_name
        )
        
        if not success:
            return self._error(
                message="게임에 참여할 수 없습니다.",
                code="JOIN_GAME_FAILED",
            )
        
        # 연결 관리자에 등록
        self.connection_manager.register_player_to_game(player_id, game_id)
        
        # 게임 상태 전송
        await self.send_game_state_to_player(player_id, game_id)
        
        # 다른 플레이어들에게 알림
        await self.broadcast_game_state(game_id)
        
        return {
            "success": True,
            "message": "게임에 참여했습니다.",
            "game_id": game_id,
        }
    
    async def handle_get_game_state(self, player_id: str, message: dict) -> Dict:
        """
        게임 상태 조회 메시지를 처리합니다.
        
        Args:
            player_id: 플레이어 ID
            message: {
                "type": "GET_GAME_STATE"
            }
            
        Returns:
            처리 결과
        """
        game_id = self.connection_manager.get_player_game(player_id)
        if not game_id:
            return self._error(
                message="플레이어가 게임에 참여하지 않았습니다.",
                code="PLAYER_NOT_IN_GAME",
            )
        
        await self.send_game_state_to_player(player_id, game_id)
        
        return {
            "success": True,
            "message": "게임 상태를 전송했습니다.",
        }
    
    async def handle_start_game(self, player_id: str, message: dict) -> Dict:
        """
        게임 시작 메시지를 처리합니다.
        
        Args:
            player_id: 플레이어 ID
            message: {
                "type": "START_GAME",
                "game_id": str (optional, 없으면 플레이어가 속한 게임 사용)
            }
            
        Returns:
            처리 결과
        """
        # game_id 확인
        game_id = message.get("game_id")
        if not game_id:
            game_id = self.connection_manager.get_player_game(player_id)
            if not game_id:
                return self._error(
                    message="게임 ID가 필요하거나 플레이어가 게임에 참여하지 않았습니다.",
                    code="GAME_ID_OR_PLAYER_REQUIRED",
                )
        
        # 게임 조회
        game = self.game_manager.get_game(game_id)
        if not game:
            return self._error(
                message="게임을 찾을 수 없습니다.",
                code="GAME_NOT_FOUND",
            )
        
        # 플레이어가 게임에 참여했는지 확인
        if not any(p.id == player_id for p in game.players):
            return self._error(
                message="플레이어가 이 게임에 참여하지 않았습니다.",
                code="PLAYER_NOT_IN_GAME",
            )
        
        # 게임 시작 시도
        success = self.game_manager.start_game(game_id)
        
        if not success:
            # 실패 원인 확인
            if game.state != GameState.WAITING:
                return self._error(
                    message="게임이 이미 시작되었거나 종료되었습니다.",
                    code="GAME_ALREADY_STARTED",
                )
            elif len(game.players) < MIN_PLAYERS:
                return self._error(
                    message=(
                        f"게임을 시작하려면 최소 {MIN_PLAYERS}명의 플레이어가 필요합니다. "
                        f"(현재: {len(game.players)}명)"
                    ),
                    code="NOT_ENOUGH_PLAYERS",
                )
            else:
                return self._error(
                    message="게임을 시작할 수 없습니다.",
                    code="START_GAME_FAILED",
                )
        
        # 게임 시작 이벤트 로그 추가
        game = self.game_manager.get_game(game_id)  # 업데이트된 게임 상태 가져오기
        game.add_event(
            f"게임이 시작되었습니다! 총 {len(game.players)}명의 플레이어가 참여합니다.",
            "notification"
        )
        
        # 모든 플레이어에게 게임 상태 전송
        await self.broadcast_game_state(game_id)
        
        return {
            "success": True,
            "message": "게임이 시작되었습니다.",
            "game_id": game_id,
        }
    
    async def handle_add_ai_player(self, player_id: str, message: dict) -> Dict:
        """
        AI 플레이어 추가 메시지를 처리합니다.
        
        Args:
            player_id: 플레이어 ID
            message: {
                "type": "ADD_AI_PLAYER",
                "game_id": str (optional, 없으면 플레이어가 속한 게임 사용),
                "count": int,  // 추가할 AI 플레이어 수
                "difficulty": str  // "easy" | "medium" | "hard"
            }
            
        Returns:
            처리 결과
        """
        # game_id 확인
        game_id = message.get("game_id")
        if not game_id:
            game_id = self.connection_manager.get_player_game(player_id)
            if not game_id:
                return self._error(
                    message="게임 ID가 필요하거나 플레이어가 게임에 참여하지 않았습니다.",
                    code="GAME_ID_OR_PLAYER_REQUIRED",
                )
        
        # 게임 조회
        game = self.game_manager.get_game(game_id)
        if not game:
            return self._error(
                message="게임을 찾을 수 없습니다.",
                code="GAME_NOT_FOUND",
            )
        
        # 플레이어가 게임에 참여했는지 확인
        if not any(p.id == player_id for p in game.players):
            return self._error(
                message="플레이어가 이 게임에 참여하지 않았습니다.",
                code="PLAYER_NOT_IN_GAME",
            )
        
        # count 확인
        count = message.get("count", 1)
        if not isinstance(count, int) or count <= 0:
            return self._error(
                message="AI 플레이어 수는 1 이상의 정수여야 합니다.",
                code="INVALID_AI_COUNT",
            )
        
        if count > MAX_PLAYERS:
            return self._error(
                message=f"AI 플레이어 수는 최대 {MAX_PLAYERS}명까지 추가할 수 있습니다.",
                code="AI_COUNT_EXCEEDS_MAX",
            )
        
        # difficulty 확인
        difficulty = message.get("difficulty", "medium")
        if difficulty not in ["easy", "medium", "hard"]:
            return self._error(
                message="난이도는 'easy', 'medium', 'hard' 중 하나여야 합니다.",
                code="INVALID_AI_DIFFICULTY",
            )
        
        # AI 플레이어 추가
        result = self.game_manager.add_ai_players_to_game(
            game_id=game_id,
            count=count,
            difficulty=difficulty,
        )
        
        if not result.get("success"):
            return self._error(
                message=result.get("message", "AI 플레이어 추가에 실패했습니다."),
                code="ADD_AI_FAILED",
            )
        
        # 모든 플레이어에게 게임 상태 전송
        await self.broadcast_game_state(game_id)
        
        return {
            "success": True,
            "message": result.get("message", f"AI 플레이어 {result.get('added_count', 0)}명이 추가되었습니다."),
            "game_id": game_id,
            "added_count": result.get("added_count", 0),
        }
    
    async def send_game_state_to_player(self, player_id: str, game_id: str) -> bool:
        """
        플레이어에게 게임 상태를 전송합니다.
        
        Args:
            player_id: 플레이어 ID
            game_id: 게임 ID
            
        Returns:
            전송 성공 여부
        """
        game_state = self.game_manager.get_game_state_dict(game_id, player_id)
        if not game_state:
            return False
        
        # 프론트엔드 요청 형식으로 메시지 구성
        message = {
            "type": "GAME_STATE_UPDATE",
            **game_state,  # gameId, players, currentTurn, turnState, events, phase
        }
        
        return await self.connection_manager.send_personal_message(message, player_id)
    
    async def broadcast_game_state(self, game_id: str) -> int:
        """
        게임의 모든 플레이어에게 게임 상태를 브로드캐스트합니다.
        
        Args:
            game_id: 게임 ID
            
        Returns:
            전송 성공한 플레이어 수
        """
        game = self.game_manager.get_game(game_id)
        if not game:
            return 0
        
        player_ids = self.connection_manager.get_game_players(game_id)
        success_count = 0
        
        for player_id in list(player_ids):
            if await self.send_game_state_to_player(player_id, game_id):
                success_count += 1
        
        return success_count
    
    async def broadcast_win_info(self, game_id: str, win_info: dict) -> int:
        """
        승리 정보를 브로드캐스트합니다.
        
        Args:
            game_id: 게임 ID
            win_info: 승리 정보
            
        Returns:
            전송 성공한 플레이어 수
        """
        message = {
            "type": "GAME_END",
            "data": win_info,
        }
        
        return await self.connection_manager.broadcast_to_game(message, game_id)

