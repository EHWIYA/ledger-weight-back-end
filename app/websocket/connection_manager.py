"""
연결 관리자 (Connection Manager)

WebSocket 연결을 관리하고 메시지를 브로드캐스트합니다.
"""

from typing import Dict, Optional, Set
from fastapi import WebSocket
from app.utils.constants import WS_MAX_CONNECTIONS


class ConnectionManager:
    """
    연결 관리자 클래스
    
    WebSocket 연결을 관리하고 메시지를 브로드캐스트합니다.
    """
    
    def __init__(self):
        """연결 관리자 초기화"""
        # 플레이어 ID -> WebSocket 연결
        self.active_connections: Dict[str, WebSocket] = {}
        # 게임 ID -> 플레이어 ID 집합
        self.game_players: Dict[str, Set[str]] = {}
        # 플레이어 ID -> 게임 ID
        self.player_games: Dict[str, str] = {}
    
    async def connect(self, websocket: WebSocket, player_id: str) -> bool:
        """
        WebSocket 연결을 수락하고 등록합니다.
        
        Args:
            websocket: WebSocket 연결
            player_id: 플레이어 ID
            
        Returns:
            연결 성공 여부
        """
        if len(self.active_connections) >= WS_MAX_CONNECTIONS:
            return False
        
        await websocket.accept()
        self.active_connections[player_id] = websocket
        return True
    
    def disconnect(self, player_id: str) -> None:
        """
        WebSocket 연결을 해제합니다.
        
        Args:
            player_id: 플레이어 ID
        """
        if player_id in self.active_connections:
            del self.active_connections[player_id]
        
        # 게임에서 플레이어 제거
        if player_id in self.player_games:
            game_id = self.player_games[player_id]
            if game_id in self.game_players:
                self.game_players[game_id].discard(player_id)
            del self.player_games[player_id]
    
    def register_player_to_game(self, player_id: str, game_id: str) -> None:
        """
        플레이어를 게임에 등록합니다.
        
        Args:
            player_id: 플레이어 ID
            game_id: 게임 ID
        """
        if game_id not in self.game_players:
            self.game_players[game_id] = set()
        
        self.game_players[game_id].add(player_id)
        self.player_games[player_id] = game_id
    
    def get_game_players(self, game_id: str) -> Set[str]:
        """
        게임에 연결된 플레이어 ID 목록을 반환합니다.
        
        Args:
            game_id: 게임 ID
            
        Returns:
            플레이어 ID 집합
        """
        return self.game_players.get(game_id, set())
    
    def get_player_game(self, player_id: str) -> Optional[str]:
        """
        플레이어가 속한 게임 ID를 반환합니다.
        
        Args:
            player_id: 플레이어 ID
            
        Returns:
            게임 ID (없으면 None)
        """
        return self.player_games.get(player_id)
    
    async def send_personal_message(self, message: dict, player_id: str) -> bool:
        """
        특정 플레이어에게 메시지를 전송합니다.
        
        Args:
            message: 전송할 메시지
            player_id: 플레이어 ID
            
        Returns:
            전송 성공 여부
        """
        if player_id not in self.active_connections:
            return False
        
        websocket = self.active_connections[player_id]
        try:
            await websocket.send_json(message)
            return True
        except Exception:
            # 연결이 끊어진 경우
            self.disconnect(player_id)
            return False
    
    async def broadcast_to_game(self, message: dict, game_id: str) -> int:
        """
        게임의 모든 플레이어에게 메시지를 브로드캐스트합니다.
        
        Args:
            message: 전송할 메시지
            game_id: 게임 ID
            
        Returns:
            전송 성공한 플레이어 수
        """
        player_ids = self.get_game_players(game_id)
        success_count = 0
        
        for player_id in list(player_ids):  # 리스트로 변환하여 순회 중 수정 방지
            if await self.send_personal_message(message, player_id):
                success_count += 1
        
        return success_count
    
    async def broadcast_to_all(self, message: dict) -> int:
        """
        모든 연결된 플레이어에게 메시지를 브로드캐스트합니다.
        
        Args:
            message: 전송할 메시지
            
        Returns:
            전송 성공한 플레이어 수
        """
        success_count = 0
        
        for player_id in list(self.active_connections.keys()):
            if await self.send_personal_message(message, player_id):
                success_count += 1
        
        return success_count
    
    def is_connected(self, player_id: str) -> bool:
        """
        플레이어가 연결되어 있는지 확인합니다.
        
        Args:
            player_id: 플레이어 ID
            
        Returns:
            연결 여부
        """
        return player_id in self.active_connections
    
    def get_connection_count(self) -> int:
        """
        현재 연결된 플레이어 수를 반환합니다.
        
        Returns:
            연결 수
        """
        return len(self.active_connections)

