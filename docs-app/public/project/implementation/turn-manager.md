# 턴 관리자 (TurnManager) 구현 문서

## 개요
게임의 턴 순서, 턴 단계, 카드 드로우 등을 관리하는 TurnManager 클래스의 구현 문서입니다.

## 구현 내용

### 파일
- `app/game/turn_manager.py` - TurnManager 클래스

## 의사결정 기록

### 1. 턴 관리자 구조
**선택한 방식**: Game과 CardManager를 의존성으로 받는 구조

**이유**:
- Game의 상태를 직접 관리
- CardManager를 통해 카드 드로우 처리
- 단일 책임 원칙 준수

**코드 예시**:
```python
class TurnManager:
    def __init__(self, game: Game, card_manager: CardManager):
        self.game = game
        self.card_manager = card_manager
```

**대안 고려**:
- GameManager 내부에 통합: 턴 관리 로직이 복잡해질 수 있음
- 별도 클래스로 분리: 현재 선택한 방식, 유지보수 용이

### 2. 턴 단계 관리
**선택한 방식**: TurnState Enum을 사용한 상태 관리

**이유**:
- 명확한 상태 전환
- 타입 안정성
- 상태별 메서드 분리 가능

**턴 단계 흐름**:
```
DRAW → PLAY_CARD → (RESPOND) → END_TURN → (다음 플레이어) DRAW
```

**코드 예시**:
```python
def process_draw_phase(self, player_id: str) -> bool:
    # 카드 드로우
    cards_drawn = self.draw_cards_for_player(player_id, 2)
    
    # PLAY_CARD 단계로 이동
    self.game.set_turn_state(TurnState.PLAY_CARD)
    return True
```

### 3. 카드 드로우 처리
**선택한 방식**: 기본 2장 드로우, 덱 비어있으면 자동 재생성

**이유**:
- BANG! 게임 규칙 준수
- 덱 재생성 자동 처리로 게임 중단 방지

**코드 예시**:
```python
def draw_cards_for_player(self, player_id: str, count: int) -> List:
    cards_drawn = []
    
    for _ in range(count):
        # 덱이 비어있으면 재생성
        if self.card_manager.get_deck_count() == 0:
            self.card_manager.reshuffle_discard_pile()
        
        card = self.card_manager.draw_card()
        if card:
            player.add_card(card)
            cards_drawn.append(card)
    
    return cards_drawn
```

### 4. 다음 플레이어 찾기
**선택한 방식**: Game 모델의 `get_next_player()` 메서드 활용

**이유**:
- 원형 구조에서 다음 플레이어 찾기 로직 재사용
- 생존 플레이어만 고려

**코드 예시**:
```python
def move_to_next_player(self) -> bool:
    next_player = self.game.get_next_player(self.game.current_player_id)
    if not next_player:
        return False
    
    self.game.turn_number += 1
    return self.start_turn(next_player.id)
```

## 주요 메서드

### 턴 시작 및 종료
- `start_turn(player_id)`: 플레이어의 턴 시작
- `end_turn(player_id)`: 플레이어의 턴 종료
- `move_to_next_player()`: 다음 플레이어로 이동

### 턴 단계 처리
- `process_draw_phase(player_id)`: 카드 드로우 단계 처리
- `can_play_card(player_id)`: 카드 사용 가능 여부 확인
- `set_respond_phase(player_id)`: 대응 단계로 설정
- `return_to_play_phase()`: 카드 사용 단계로 복귀

### 카드 드로우
- `draw_cards_for_player(player_id, count)`: 플레이어에게 카드 드로우

### 조회
- `get_current_player()`: 현재 턴 플레이어 조회
- `get_next_player()`: 다음 턴 플레이어 조회
- `is_player_turn(player_id)`: 플레이어의 턴 여부 확인
- `get_turn_info()`: 현재 턴 정보 반환

## 사용 예시

```python
from app.game.turn_manager import TurnManager
from app.game.game_manager import GameManager
from app.game.card_manager import CardManager

# 게임 매니저에서 게임 생성
game_manager = GameManager()
game = game_manager.create_game()
game_manager.start_game(game.id)

# 턴 관리자 생성
card_manager = game_manager.get_card_manager(game.id)
turn_manager = TurnManager(game, card_manager)

# 첫 번째 플레이어 턴 시작
first_player = game.players[0]
turn_manager.start_turn(first_player.id)

# 카드 사용 가능 여부 확인
if turn_manager.can_play_card(first_player.id):
    # 카드 사용 로직...

# 턴 종료
turn_manager.end_turn(first_player.id)
# 자동으로 다음 플레이어 턴 시작
```

## 트러블슈팅

### 이슈: 덱이 비어있을 때 처리
**문제**: 카드 드로우 중 덱이 비어있으면 게임이 중단될 수 있음

**해결**: 
- 드로우 전 덱 상태 체크
- 비어있으면 버림 더미 재생성
- 재생성 후에도 비어있으면 드로우 중단

**코드**:
```python
if self.card_manager.get_deck_count() == 0:
    self.card_manager.reshuffle_discard_pile()
    if self.card_manager.get_deck_count() == 0:
        break  # 더 이상 드로우 불가
```

### 이슈: 핸드 카드 수 제한
**문제**: 재력보다 많은 카드를 보유할 수 없음 (BANG! 규칙)

**해결**: 
- 턴 종료 시 핸드 카드 수 체크
- 초과 시 버리기 로직 필요 (향후 구현)

**코드**:
```python
def end_turn(self, player_id: str) -> bool:
    player = self.game.get_player(player_id)
    max_hand_size = player.hp
    
    if player.get_hand_count() > max_hand_size:
        # TODO: 초과 카드 버리기 로직
        pass
```

## 성능 고려사항

### 1. 턴 전환 최적화
- 다음 플레이어 찾기: O(n) 시간 복잡도 (n = 플레이어 수)
- 플레이어 수가 적어서 성능 문제 없음

### 2. 카드 드로우 최적화
- 덱 재생성은 필요 시에만 수행
- 드로우는 O(1) 시간 복잡도 (리스트 pop)

### 3. 상태 관리
- Game 모델의 상태를 직접 수정
- 불필요한 복사 최소화

### 4. 향후 개선 가능 사항
- 턴 히스토리 저장 (선택적)
- 턴 시간 제한 기능 (필요시)
- 자동 턴 종료 (타임아웃)

## 턴 플로우

### 정상 턴 플로우
1. **DRAW 단계**: 카드 2장 드로우
2. **PLAY_CARD 단계**: 카드 사용 (여러 번 가능)
3. **END_TURN**: 턴 종료
4. **다음 플레이어**: 자동으로 다음 플레이어 턴 시작

### 공격 받을 때 플로우
1. **PLAY_CARD 단계**: 공격 카드 사용
2. **RESPOND 단계**: 대상 플레이어가 방어
3. **PLAY_CARD 단계**: 원래 플레이어로 복귀 (방어 성공 시)
4. **END_TURN**: 턴 종료

## 다음 단계
- [ ] 액션 핸들러 구현 (ActionHandler)
- [ ] 카드 사용 로직 구현
- [ ] 공격/방어 메커니즘 구현
- [ ] 핸드 카드 수 제한 처리

