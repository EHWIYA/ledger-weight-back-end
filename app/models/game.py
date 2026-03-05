"""
게임 (Game) 모델
"""

from typing import List, Dict, Optional
from pydantic import BaseModel, Field
from app.models.player import Player
from app.models.card import Card
from app.utils.constants import GameState, TurnState, Role as RoleEnum


class Game(BaseModel):
    """
    게임 모델
    
    게임 전체 상태를 관리합니다.
    """
    
    id: str = Field(..., description="게임 고유 ID")
    state: GameState = Field(GameState.WAITING, description="게임 상태")
    players: List[Player] = Field(default_factory=list, description="플레이어 목록")
    deck: List[Card] = Field(default_factory=list, description="덱 (카드 더미)")
    discard_pile: List[Card] = Field(default_factory=list, description="버림 더미")
    current_player_id: Optional[str] = Field(None, description="현재 턴 플레이어 ID")
    turn_state: TurnState = Field(TurnState.DRAW, description="턴 상태")
    turn_number: int = Field(0, description="턴 번호")
    last_event: Optional[str] = Field(None, description="마지막 이벤트 메시지")
    events: List[Dict] = Field(default_factory=list, description="게임 이벤트 로그 (최근 50개)")
    treasure_counters: Dict[str, Dict[str, int]] = Field(
        default_factory=dict,
        description="보물 효과 카운터 (플레이어별)",
    )
    turn_attack_counters: Dict[str, int] = Field(
        default_factory=dict,
        description="플레이어별 이번 턴 정산 사용 횟수",
    )
    defending_player_id: Optional[str] = Field(
        None,
        description="현재 공격에 대해 방어해야 하는 플레이어 ID",
    )
    pending_required_missed: int = Field(
        1,
        description="현재 공격에 대해 필요한 회피 카드 수 (낙인 인장 등 보물 적용 후)",
    )
    pending_used_missed: int = Field(
        0,
        description="현재 공격에 대해 이미 사용한 회피 카드 수",
    )
    required_response: Optional[Dict] = Field(
        None,
        description="프론트엔드에 요청할 응답 정보 (requiredResponse)",
    )
    pending_action: Optional[Dict] = Field(
        None,
        description="선택 응답이 필요한 액션의 서버 내부 컨텍스트",
    )
    
    class Config:
        arbitrary_types_allowed = True
        use_enum_values = True
    
    def add_player(self, player: Player) -> bool:
        """
        플레이어를 게임에 추가합니다.
        
        Args:
            player: 추가할 플레이어
            
        Returns:
            추가 성공 여부
        """
        if len(self.players) >= 7:  # 최대 7명
            return False
        
        if any(p.id == player.id for p in self.players):
            return False  # 이미 존재하는 플레이어
        
        self.players.append(player)
        return True
    
    def remove_player(self, player_id: str) -> Optional[Player]:
        """
        플레이어를 게임에서 제거합니다.
        
        Args:
            player_id: 제거할 플레이어 ID
            
        Returns:
            제거된 플레이어 (없으면 None)
        """
        for i, player in enumerate(self.players):
            if player.id == player_id:
                return self.players.pop(i)
        return None
    
    def get_player(self, player_id: str) -> Optional[Player]:
        """
        플레이어를 조회합니다.
        
        Args:
            player_id: 플레이어 ID
            
        Returns:
            플레이어 (없으면 None)
        """
        for player in self.players:
            if player.id == player_id:
                return player
        return None
    
    def get_alive_players(self) -> List[Player]:
        """생존한 플레이어 목록을 반환합니다."""
        return [p for p in self.players if p.is_alive]
    
    def get_player_by_position(self, position: int) -> Optional[Player]:
        """
        위치로 플레이어를 조회합니다.
        
        Args:
            position: 플레이어 위치
            
        Returns:
            플레이어 (없으면 None)
        """
        for player in self.players:
            if player.position == position:
                return player
        return None
    
    def get_next_player(self, current_player_id: str) -> Optional[Player]:
        """
        다음 플레이어를 반환합니다.
        
        Args:
            current_player_id: 현재 플레이어 ID
            
        Returns:
            다음 플레이어 (없으면 None)
        """
        current_player = self.get_player(current_player_id)
        if not current_player:
            return None
        
        alive_players = self.get_alive_players()
        if len(alive_players) <= 1:
            return None
        
        # 현재 플레이어의 다음 위치 찾기
        current_pos = current_player.position
        positions = sorted([p.position for p in alive_players])
        
        try:
            current_index = positions.index(current_pos)
            next_index = (current_index + 1) % len(positions)
            next_position = positions[next_index]
            return self.get_player_by_position(next_position)
        except (ValueError, IndexError):
            return None
    
    def calculate_distance(self, from_player: Player, to_player: Player) -> int:
        """
        두 플레이어 간의 거리를 계산합니다.
        
        - 기본적으로 테이블을 원형으로 보고 위치 차이로 거리를 계산합니다.
        - 보물 효과:
          - 만국 지도(공격자): 모든 상대와의 거리 -1
          - 안개 병풍(방어자): 다른 플레이어가 나를 볼 때 거리 +1
        
        Args:
            from_player: 출발 플레이어 (공격자 등)
            to_player: 도착 플레이어 (대상)
            
        Returns:
            거리 (최소 1)
        """
        if from_player.id == to_player.id:
            return 0
        
        total_players = len(self.players)
        pos_diff = abs(from_player.position - to_player.position)
        
        # 원형 구조이므로 양방향 거리 중 작은 값
        distance = min(pos_diff, total_players - pos_diff)
        
        # 보물/장착 효과 적용
        # 만국 지도: 공격자가 보는 모든 거리를 1 감소
        if getattr(from_player, "treasure", None) == "만국 지도":
            distance -= 1
        
        # 안개 병풍: 다른 플레이어가 나를 볼 때 거리를 1 증가
        if getattr(to_player, "treasure", None) == "안개 병풍":
            distance += 1
        
        # 세력권 경계(Mustang): 다른 플레이어가 나를 볼 때 거리를 1 증가
        equipment = getattr(to_player, "equipment", {}) or {}
        if "mustang" in equipment:
            distance += 1
        
        return max(1, distance)  # 최소 거리는 1
    
    def draw_card(self, player_id: str) -> Optional[Card]:
        """
        플레이어가 카드를 뽑습니다.
        
        Args:
            player_id: 플레이어 ID
            
        Returns:
            뽑은 카드 (덱이 비어있으면 None)
        """
        if not self.deck:
            return None
        
        card = self.deck.pop(0)
        player = self.get_player(player_id)
        if player:
            player.add_card(card)
        return card
    
    def discard_card(self, card: Card) -> None:
        """카드를 버림 더미에 추가합니다."""
        self.discard_pile.append(card)
    
    def set_current_player(self, player_id: str) -> None:
        """현재 턴 플레이어를 설정합니다."""
        self.current_player_id = player_id
    
    def set_turn_state(self, state: TurnState) -> None:
        """턴 상태를 설정합니다."""
        self.turn_state = state
    
    def add_event(self, event: str, event_type: str = "action") -> None:
        """
        이벤트 메시지를 추가합니다.
        
        Args:
            event: 이벤트 메시지
            event_type: 이벤트 타입 ("action" | "notification" | "error")
        """
        import time
        self.last_event = event
        
        # 이벤트 로그에 추가
        event_dict = {
            "id": f"event_{len(self.events)}_{int(time.time() * 1000)}",
            "timestamp": int(time.time() * 1000),  # Unix timestamp (밀리초)
            "message": event,
            "type": event_type,
        }
        self.events.append(event_dict)
        
        # 최근 50개만 유지
        if len(self.events) > 50:
            self.events = self.events[-50:]
    
    def to_dict(self, player_id: Optional[str] = None) -> dict:
        """
        딕셔너리로 변환 (WebSocket 전송용 - 프론트엔드 요청 형식)
        
        Args:
            player_id: 조회하는 플레이어 ID (자신의 핸드는 보이고, 다른 플레이어는 숨김)
            
        Returns:
            게임 상태 딕셔너리 (프론트엔드 요청 형식)
        """
        # phase 결정
        if self.state == GameState.WAITING:
            phase = "lobby"
        elif self.state == GameState.IN_PROGRESS:
            phase = "playing"
        elif self.state == GameState.FINISHED:
            phase = "finished"
        else:
            phase = "lobby"
        
        # turnState 구성
        turn_state = {
            "currentTurn": self.current_player_id or "",
            "timeLeft": 60,  # TODO: 실제 타이머 구현 시 수정
        }
        
        # requiredResponse 설정 (모든 유형 공통)
        if self.required_response:
            turn_state["requiredResponse"] = self.required_response
        
        return {
            "gameId": self.id,
            "players": [
                player.to_dict(hide_hand=(player.id != player_id))
                for player in self.players
            ],
            "currentTurn": self.current_player_id or "",
            "turnState": turn_state,
            "events": self.events[-50:],  # 최근 50개 이벤트
            "phase": phase,
        }
    
    def __str__(self) -> str:
        state_str = self.state.value if hasattr(self.state, 'value') else str(self.state)
        return f"Game(id={self.id}, state={state_str}, players={len(self.players)})"
    
    def __repr__(self) -> str:
        state_str = self.state.value if hasattr(self.state, 'value') else str(self.state)
        return f"Game(id={self.id}, state={state_str})"

