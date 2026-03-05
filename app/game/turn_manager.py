"""
턴 관리자 (Turn Manager)

게임의 턴 순서, 턴 단계, 카드 드로우 등을 관리합니다.
"""

from typing import Optional, Dict, List
from app.models.game import Game
from app.models.player import Player
from app.game.card_manager import CardManager
from app.utils.constants import TurnState, GameState, Suit


class TurnManager:
    """
    턴 관리자 클래스
    
    게임의 턴 순서와 단계를 관리합니다.
    """
    
    def __init__(self, game: Game, card_manager: CardManager):
        """
        턴 관리자 초기화
        
        Args:
            game: Game 인스턴스
            card_manager: CardManager 인스턴스
        """
        self.game = game
        self.card_manager = card_manager
    
    def start_turn(self, player_id: str) -> bool:
        """
        플레이어의 턴을 시작합니다.
        
        Args:
            player_id: 턴을 시작할 플레이어 ID
            
        Returns:
            시작 성공 여부
        """
        player = self.game.get_player(player_id)
        if not player or not player.is_alive:
            return False
        
        if self.game.state != GameState.IN_PROGRESS:
            return False
        
        # 영업 금지(Jail) 처리: 턴 시작 전에 판정 수행
        jail_card = player.equipment.get("jail") if hasattr(player, "equipment") else None
        if jail_card:
            # 영업 금지 카드는 판정 후 버림
            removed_jail = player.equipment.pop("jail", None)
            if removed_jail:
                self.card_manager.discard_card(removed_jail)
            
            # 판정 카드 1장 뽑기 (문양이 '치유'(HEARTS)면 성공, 아니면 실패)
            if self.card_manager.get_deck_count() == 0:
                self.card_manager.reshuffle_discard_pile()
            
            judgement_success = False
            judgement_card = self.card_manager.draw_card()
            if judgement_card:
                self.card_manager.discard_card(judgement_card)
                if judgement_card.suit == Suit.HEARTS:
                    judgement_success = True
            
            if not judgement_success:
                # 판정 실패: 이 턴 전체를 건너뛰고 다음 플레이어로 이동
                self.game.set_current_player(player.id)
                self.game.set_turn_state(TurnState.END_TURN)
                self.game.add_event(
                    f"{player.name}이(가) 영업 금지 판정에 실패하여 이번 턴을 건너뜁니다.",
                    "action",
                )
                return self.move_to_next_player()
        
        # 턴별 정산/보호 관련 상태 초기화
        self.game.turn_attack_counters.clear()
        self.game.defending_player_id = None
        self.game.pending_required_missed = 1
        self.game.pending_used_missed = 0
        self.game.required_response = None
        self.game.pending_action = None
        
        # 현재 플레이어 설정
        self.game.set_current_player(player_id)
        self.game.set_turn_state(TurnState.DRAW)
        
        # 기록 파편 (페드로 라미레스):
        # 내 턴 시작 시, 버려진 카드 더미 맨 위가 '돈' 문양이면 손패로 가져올 수 있음.
        treasure = getattr(player, "treasure", None)
        if treasure == "기록 파편":
            top_card = self.card_manager.get_discard_top()
            if top_card and top_card.suit == Suit.DIAMONDS:
                taken = self.card_manager.take_discard_top()
                if taken:
                    player.add_card(taken)
                    self.game.add_event(
                        f"{player.name}이(가) 기록 파편 효과로 버림 더미에서 카드를 회수했습니다.",
                        "action",
                    )
        
        # 카드 드로우 단계로 이동
        return self.process_draw_phase(player_id)
    
    def process_draw_phase(self, player_id: str) -> bool:
        """
        카드 드로우 단계를 처리합니다.
        
        Args:
            player_id: 플레이어 ID
            
        Returns:
            처리 성공 여부
        """
        if self.game.current_player_id != player_id:
            return False
        
        if self.game.turn_state != TurnState.DRAW:
            return False
        
        player = self.game.get_player(player_id)
        if not player or not player.is_alive:
            return False
        
        # 기본 드로우/보물 효과 처리
        treasure = getattr(player, "treasure", None)
        cards_drawn: List = []
        
        # 우선 전표 (킷 카를슨): 덱 상단 3장 보고 1장 선택, 1장은 맨 위, 1장은 맨 아래
        if treasure == "우선 전표":
            # 덱에서 최대 3장까지 임시로 뽑음
            temp_cards: List = []
            for _ in range(3):
                if self.card_manager.get_deck_count() == 0:
                    self.card_manager.reshuffle_discard_pile()
                    if self.card_manager.get_deck_count() == 0:
                        break
                card = self.card_manager.draw_card()
                if not card:
                    break
                temp_cards.append(card)
            
            if not temp_cards:
                # 덱이 비어있으면 기본 드로우도 불가, 그냥 종료
                return True
            
            # 서버 내부 컨텍스트 저장
            self.game.pending_action = {
                "type": "SELECT_DRAW_ORDER",
                "player_id": player_id,
                "cards": temp_cards,
            }
            
            # 클라이언트에 노출할 후보 카드 정보 구성
            candidate_cards = []
            for c in temp_cards:
                suit_val = c.suit.value if (c.suit and hasattr(c.suit, "value")) else (c.suit if c.suit else None)
                rank_val = c.rank.value if (c.rank and hasattr(c.rank, "value")) else (c.rank if c.rank else None)
                candidate_cards.append(
                    {
                        "id": c.id,
                        "name": c.name,
                        "suit": suit_val,
                        "rank": rank_val,
                    }
                )
            
            self.game.required_response = {
                "type": "SELECT_DRAW_ORDER",
                "source": "우선 전표",
                "candidateCards": candidate_cards,
            }
            
            # 드로우 단계 유지, 선택 응답을 기다림
            return True
        
        if treasure == "황금 주판":
            # 황금 주판 (블랙 잭):
            # 두 번째 드로우 카드가 '돈' 문양이면 1장 더 드로우 (공개).
            first = self.draw_cards_for_player(player_id, 1)
            second = self.draw_cards_for_player(player_id, 1)
            cards_drawn.extend(first)
            cards_drawn.extend(second)
            
            second_card = second[0] if second else None
            if second_card and second_card.suit == Suit.DIAMONDS:
                extra = self.draw_cards_for_player(player_id, 1)
                cards_drawn.extend(extra)
                if extra:
                    self.game.add_event(
                        f"{player.name}의 황금 주판 효과로 추가로 카드를 1장 공개 드로우했습니다.",
                        "action",
                    )
        else:
            # 기본 드로우: 2장
            cards_drawn = self.draw_cards_for_player(player_id, 2)
        
        if cards_drawn:
            self.game.add_event(f"{player.name}이(가) 카드 {len(cards_drawn)}장을 뽑았습니다.", "action")
        
        # 카드 사용 단계로 이동
        self.game.set_turn_state(TurnState.PLAY_CARD)
        return True
    
    def draw_cards_for_player(self, player_id: str, count: int) -> List:
        """
        플레이어에게 카드를 드로우합니다.
        
        Args:
            player_id: 플레이어 ID
            count: 드로우할 카드 수
            
        Returns:
            드로우한 카드 목록
        """
        player = self.game.get_player(player_id)
        if not player:
            return []
        
        cards_drawn = []
        
        for _ in range(count):
            # 덱이 비어있으면 재생성
            if self.card_manager.get_deck_count() == 0:
                self.card_manager.reshuffle_discard_pile()
                # 재생성 후에도 비어있으면 종료
                if self.card_manager.get_deck_count() == 0:
                    break
            
            card = self.card_manager.draw_card()
            if card:
                player.add_card(card)
                cards_drawn.append(card)
        
        return cards_drawn
    
    def can_end_turn(self, player_id: str) -> bool:
        """
        플레이어가 턴을 종료할 수 있는지 확인합니다.
        
        Args:
            player_id: 플레이어 ID
            
        Returns:
            턴 종료 가능 여부
        """
        if self.game.current_player_id != player_id:
            return False
        
        if self.game.turn_state not in [TurnState.PLAY_CARD, TurnState.RESPOND]:
            return False
        
        return True
    
    def end_turn(self, player_id: str) -> bool:
        """
        플레이어의 턴을 종료합니다.
        
        Args:
            player_id: 플레이어 ID
            
        Returns:
            종료 성공 여부
        """
        if not self.can_end_turn(player_id):
            return False
        
        player = self.game.get_player(player_id)
        if not player:
            return False
        
        # 핸드 카드 수 제한 체크 (재력보다 많으면 버려야 함)
        max_hand_size = player.hp
        hand_count = player.get_hand_count()
        if hand_count > max_hand_size:
            # 초과 카드 자동 버리기: 손패 뒤에서부터 버림 더미로 이동
            excess = hand_count - max_hand_size
            # 현재 손패 스냅샷 기준으로 뒤에서부터 초과분 선택
            hand_snapshot = list(player.hand)
            cards_to_discard = hand_snapshot[-excess:]
            
            discarded_count = 0
            for card in cards_to_discard:
                removed = player.remove_card(card.id)
                if removed:
                    self.card_manager.discard_card(removed)
                    discarded_count += 1
            
            if discarded_count > 0:
                self.game.add_event(
                    f"{player.name}이(가) 최대 손패 제한을 초과하여 카드 {discarded_count}장을 버렸습니다.",
                    "action",
                )
        
        # 턴 종료 상태로 변경
        self.game.set_turn_state(TurnState.END_TURN)
        self.game.add_event(f"{player.name}의 턴이 종료되었습니다.", "notification")
        
        # 다음 플레이어로 이동
        return self.move_to_next_player()
    
    def move_to_next_player(self) -> bool:
        """
        다음 플레이어로 턴을 이동합니다.
        
        Returns:
            이동 성공 여부
        """
        if not self.game.current_player_id:
            return False
        
        # 다음 플레이어 찾기
        next_player = self.game.get_next_player(self.game.current_player_id)
        
        if not next_player:
            return False
        
        # 턴 번호 증가
        self.game.turn_number += 1
        
        # 다음 플레이어의 턴 시작
        return self.start_turn(next_player.id)
    
    def get_current_player(self) -> Optional[Player]:
        """
        현재 턴 플레이어를 반환합니다.
        
        Returns:
            현재 플레이어 (없으면 None)
        """
        if not self.game.current_player_id:
            return None
        return self.game.get_player(self.game.current_player_id)
    
    def get_next_player(self) -> Optional[Player]:
        """
        다음 턴 플레이어를 반환합니다 (턴을 이동하지 않음).
        
        Returns:
            다음 플레이어 (없으면 None)
        """
        if not self.game.current_player_id:
            return None
        return self.game.get_next_player(self.game.current_player_id)
    
    def is_player_turn(self, player_id: str) -> bool:
        """
        플레이어의 턴인지 확인합니다.
        
        Args:
            player_id: 플레이어 ID
            
        Returns:
            플레이어의 턴 여부
        """
        return self.game.current_player_id == player_id
    
    def can_play_card(self, player_id: str) -> bool:
        """
        플레이어가 카드를 사용할 수 있는지 확인합니다.
        
        Args:
            player_id: 플레이어 ID
            
        Returns:
            카드 사용 가능 여부
        """
        if not self.is_player_turn(player_id):
            return False
        
        if self.game.turn_state != TurnState.PLAY_CARD:
            return False
        
        player = self.game.get_player(player_id)
        if not player or not player.is_alive:
            return False
        
        return True
    
    def set_respond_phase(self, player_id: str, required_missed: int = 1) -> bool:
        """
        대응 단계로 설정합니다 (공격 받을 때).
        
        Args:
            player_id: 대응할 플레이어 ID
            
        Returns:
            설정 성공 여부
        """
        player = self.game.get_player(player_id)
        if not player or not player.is_alive:
            return False
        
        self.game.set_turn_state(TurnState.RESPOND)
        self.game.defending_player_id = player_id
        self.game.pending_required_missed = max(1, required_missed)
        self.game.pending_used_missed = 0
        # 프론트에 전달할 응답 정보 설정
        self.game.required_response = {
            "type": "RESPOND_ATTACK",
            "targetId": player_id,
            "requiredMissed": self.game.pending_required_missed,
            "usedMissed": 0,
            "message": f"{player.name}이(가) 공격을 받았습니다. 회피하시겠습니까?",
        }
        return True
    
    def return_to_play_phase(self) -> bool:
        """
        카드 사용 단계로 돌아갑니다 (대응 후).
        
        Returns:
            설정 성공 여부
        """
        if not self.game.current_player_id:
            return False
        
        # 대응 관련 상태 초기화
        self.game.set_turn_state(TurnState.PLAY_CARD)
        self.game.defending_player_id = None
        self.game.pending_required_missed = 1
        self.game.pending_used_missed = 0
        self.game.required_response = None
        self.game.pending_action = None
        return True
    
    def get_turn_info(self) -> Dict:
        """
        현재 턴 정보를 반환합니다.
        
        Returns:
            턴 정보 딕셔너리
        """
        current_player = self.get_current_player()
        next_player = self.get_next_player()
        
        return {
            "turn_number": self.game.turn_number,
            "current_player_id": self.game.current_player_id,
            "current_player_name": current_player.name if current_player else None,
            "next_player_id": next_player.id if next_player else None,
            "next_player_name": next_player.name if next_player else None,
            "turn_state": self.game.turn_state.value,
        }

