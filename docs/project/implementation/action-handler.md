# 액션 핸들러 (ActionHandler) 구현 문서

## 개요
플레이어의 액션(카드 사용, 공격 대응 등)을 처리하는 ActionHandler 클래스의 구현 문서입니다.

## 구현 내용

### 파일
- `app/game/action_handler.py` - ActionHandler 클래스

## 의사결정 기록

### 1. 액션 핸들러 구조
**선택한 방식**: Game, TurnManager, CardManager를 의존성으로 받는 구조

**이유**:
- 각 컴포넌트의 책임 분리
- 테스트 용이성
- 유연한 구조

**코드 예시**:
```python
class ActionHandler:
    def __init__(
        self,
        game: Game,
        turn_manager: TurnManager,
        card_manager: CardManager,
    ):
        self.game = game
        self.turn_manager = turn_manager
        self.card_manager = card_manager
```

**대안 고려**:
- GameManager 내부에 통합: 복잡도 증가
- 별도 클래스로 분리: 현재 선택한 방식, 유지보수 용이

### 2. 액션 처리 방식
**선택한 방식**: 액션 타입별 메서드 분리

**이유**:
- 명확한 책임 분리
- 확장 용이
- 디버깅 용이

**코드 예시**:
```python
def handle_action(self, action_type: ActionType, player_id: str, data: Dict) -> Dict:
    if action_type == ActionType.USE_CARD:
        return self.handle_use_card(player_id, data)
    elif action_type == ActionType.RESPOND_ATTACK:
        return self.handle_respond_attack(player_id, data)
    elif action_type == ActionType.END_TURN:
        return self.handle_end_turn(player_id)
```

### 3. 카드 타입별 처리
**선택한 방식**: 카드 타입별 전용 메서드

**이유**:
- 각 카드의 고유 로직 분리
- 확장 용이
- 코드 가독성 향상

**코드 예시**:
```python
if card.is_bang():
    return self.handle_bang_card(player_id, card, target_id)
elif card.is_beer():
    return self.handle_beer_card(player_id, card)
```

### 4. 공격/방어 메커니즘
**선택한 방식**: 공격 시 대응 단계로 전환, 방어 성공 시 원래 단계로 복귀

**이유**:
- BANG! 게임 규칙 준수
- 명확한 상태 전환
- 플레이어 간 상호작용 지원

**코드 예시**:
```python
def handle_bang_card(self, player_id: str, card: Card, target_id: str) -> Dict:
    # 공격 처리
    self.turn_manager.set_respond_phase(target_id)
    # 대응 단계로 설정
```

## 주요 메서드

### 액션 처리
- `handle_action(action_type, player_id, data)`: 액션 처리 (메인 진입점)
- `handle_use_card(player_id, data)`: 카드 사용 처리
- `handle_respond_attack(player_id, data)`: 공격 대응 처리
- `handle_end_turn(player_id)`: 턴 종료 처리

### 카드 타입별 처리
- `handle_bang_card(player_id, card, target_id)`: 정산 카드 처리
- `handle_beer_card(player_id, card)`: 비상금 카드 처리
- `handle_respond_attack_failed(player_id)`: 공격 대응 실패 처리

### 검증
- `validate_action(action_type, player_id, data)`: 액션 유효성 검증

## 사용 예시

```python
from app.game.action_handler import ActionHandler
from app.game.game_manager import GameManager
from app.game.turn_manager import TurnManager

# 게임 매니저에서 게임 생성
game_manager = GameManager()
game = game_manager.create_game()
game_manager.start_game(game.id)

# 턴 관리자 및 액션 핸들러 생성
card_manager = game_manager.get_card_manager(game.id)
turn_manager = TurnManager(game, card_manager)
action_handler = ActionHandler(game, turn_manager, card_manager)

# 정산 카드 사용
result = action_handler.handle_action(
    ActionType.USE_CARD,
    "player_1",
    {
        "card_id": "bang_001",
        "target_id": "player_2"
    }
)

# 공격 대응
result = action_handler.handle_action(
    ActionType.RESPOND_ATTACK,
    "player_2",
    {
        "card_id": "missed_001"
    }
)

# 턴 종료
result = action_handler.handle_action(
    ActionType.END_TURN,
    "player_1",
    {}
)
```

## 트러블슈팅

### 이슈: 공격 거리 검증
**문제**: 플레이어의 유효 영향력과 대상까지의 거리를 비교해야 함

**해결**: 
- `attacker.get_effective_range()`로 유효 영향력 계산
- `game.calculate_distance()`로 거리 계산
- 비교하여 공격 가능 여부 판단

**코드**:
```python
distance = self.game.calculate_distance(attacker, target)
effective_range = attacker.get_effective_range()

if effective_range < distance:
    return {"success": False, "message": "거리가 너무 멉니다."}
```

### 이슈: 대응 단계 후 복귀
**문제**: 공격 대응 후 원래 플레이어의 턴으로 복귀해야 함

**해결**: 
- `turn_manager.return_to_play_phase()`로 PLAY_CARD 단계로 복귀
- 현재 플레이어 ID 유지

**코드**:
```python
# 대응 성공 후
self.turn_manager.return_to_play_phase()
```

### 이슈: 재력 최대치 확인
**문제**: 비상금 사용 시 재력이 이미 최대치면 사용 불가

**해결**: 
- 사용 전 재력 확인
- 최대치면 에러 반환

**코드**:
```python
if player.hp >= player.max_hp:
    return {"success": False, "message": "재력이 이미 최대치입니다."}
```

## 성능 고려사항

### 1. 액션 검증 최적화
- `validate_action()`으로 사전 검증
- 불필요한 처리 방지

### 2. 카드 조회 최적화
- Player 모델의 `get_card()` 메서드 사용
- O(n) 시간 복잡도 (n = 핸드 카드 수)
- 핸드 카드 수가 적어서 성능 문제 없음

### 3. 거리 계산 최적화
- Game 모델의 `calculate_distance()` 메서드 사용
- O(1) 시간 복잡도

### 4. 향후 개선 가능 사항
- 액션 히스토리 저장 (선택적)
- 액션 로깅 (디버깅용)
- 액션 재현 기능 (테스트용)

## 구현된 카드 타입

### 완료
- ✅ **정산 (Bang!)**: 기본 공격 카드
- ✅ **회피 (Missed!)**: 공격 방어 카드
- ✅ **비상금 (Beer)**: 재력 회복 카드

### 예정
- ⏳ 전원 견제 (Gatling)
- ⏳ 패거리 습격 (Indians)
- ⏳ 승부 (Duel)
- ⏳ 무기 카드 (Volcanic, Winchester)
- ⏳ 장착 카드 (Scope, Barrel, Mustang, Jail)
- ⏳ 특수 카드 (Panic, Saloon, General Store)

## 액션 처리 플로우

### 정산 카드 사용 플로우
1. 액션 검증 (플레이어 턴, 카드 존재, 대상 존재)
2. 거리 및 영향력 확인
3. 카드 제거 및 버리기
4. 대응 단계로 설정
5. 이벤트 메시지 생성

### 공격 대응 플로우
1. 액션 검증 (대응 단계, 회피 카드 존재)
2. 카드 제거 및 버리기
3. 원래 플레이어 턴으로 복귀
4. 이벤트 메시지 생성

### 비상금 카드 사용 플로우
1. 액션 검증 (플레이어 턴, 카드 존재, 재력 미최대)
2. 카드 제거 및 버리기
3. 재력 회복
4. 이벤트 메시지 생성

## 다음 단계
- [ ] 나머지 카드 타입 구현
- [ ] 보물 능력 통합
- [ ] WebSocket 통신 통합
- [ ] 액션 처리 테스트

