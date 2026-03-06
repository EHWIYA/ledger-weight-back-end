# 게임 매니저 (GameManager) 구현 문서

## 개요
게임의 생성, 초기화, 상태 관리, 승리 조건 체크 등을 담당하는 GameManager 클래스의 구현 문서입니다.

## 구현 내용

### 파일
- `app/game/game_manager.py` - GameManager 클래스

## 의사결정 기록

### 1. 게임 인스턴스 관리 방식
**선택한 방식**: 딕셔너리로 게임 인스턴스 관리 (인메모리)

**이유**:
- 빠른 조회 (O(1))
- 간단한 구현
- 게임 세션은 일시적이므로 DB 불필요

**코드 예시**:
```python
def __init__(self):
    self.games: Dict[str, Game] = {}  # 게임 ID -> Game 인스턴스
    self.card_managers: Dict[str, CardManager] = {}  # 게임 ID -> CardManager
```

**대안 고려**:
- 데이터베이스 저장: 게임 히스토리 저장이 필요할 때만 고려
- Redis: 향후 확장 시 고려 가능

### 2. 역할 배정 방식
**선택한 방식**: 플레이어 수에 따른 고정 역할 구성 + **모든 플레이어 역할 완전 랜덤 배정**

**이유**:
- BANG! 게임 규칙 준수
- 게임 밸런스 유지
- 상단주 위치를 고정하지 않고, 모든 플레이어의 역할을 셔플하여 심리전/리플레이 가치를 높이기 위함

**코드 예시**:
```python
def _assign_roles(self, game: Game) -> None:
    player_count = len(game.players)
    
    if player_count == 4:
        roles = [SHERIFF, DEPUTY, OUTLAW, RENEGADE]
    elif player_count == 5:
        roles = [SHERIFF, DEPUTY, OUTLAW, OUTLAW, RENEGADE]
    # ... 나머지 구성

    # 모든 역할 완전 셔플 (상단주 고정 없음)
    random.shuffle(roles)
    final_roles = roles
```

### 3. 초기 카드 분배
**선택한 방식**: 플레이어 수에 따라 초기 카드 수 결정

**이유**:
- BANG! 게임 규칙 준수
- 게임 밸런스 유지

**코드 예시**:
```python
def _deal_initial_cards(self, game: Game, card_manager: CardManager) -> None:
    for player in game.players:
        # 4명 이하: 4장, 5명 이상: 5장
        initial_cards = 4 if len(game.players) <= 4 else 5
        cards = card_manager.draw_cards(initial_cards)
        for card in cards:
            player.add_card(card)
```

### 4. 승리 조건 체크
**선택한 방식**: 매 턴 종료 시 승리 조건 체크

**이유**:
- 게임 종료 즉시 감지
- 승리 조건 명확화

**승리 조건**:
1. **상단주 팀 승리**: 상단주가 생존해 있고, 적도 세력이 모두 사망했으며, 상단주와 야망가의 1대1 상황이 아닌 경우
2. **적도 세력 승리**: 상단주 사망 (야망가 생존 여부와 무관)
3. **야망가 승리**: 적도 세력이 모두 사망한 상태에서, 상단주와 야망가만 1대1로 남아 있고, 야망가가 마지막까지 생존한 경우

**코드 예시**:
```python
def check_win_condition(self, game_id: str) -> Optional[Dict[str, any]]:
    # 상단주 확인
    sheriff = next((p for p in alive_players if p.role.is_sheriff), None)
    
    if not sheriff:
        # 상단주 사망 - 적도 세력 승리
        return {"winner_id": outlaws[0].id, "winner_role": "적도 세력"}
    
    # 적도 세력 모두 사망 - 상단주 팀 승리
    if not outlaws:
        return {"winner_id": sheriff.id, "winner_role": "상단주"}
```

## 주요 메서드

### 게임 생성 및 관리
- `create_game(game_id)`: 새 게임 생성
- `get_game(game_id)`: 게임 조회
- `remove_game(game_id)`: 게임 제거
- `list_games()`: 모든 게임 목록 조회

### 플레이어 관리
- `add_player_to_game(game_id, player_id, player_name)`: 플레이어 추가
- `start_game(game_id)`: 게임 시작 (역할 배정, 카드 분배)

### 게임 상태
- `get_game_state_dict(game_id, player_id)`: 게임 상태 딕셔너리 반환
- `check_win_condition(game_id)`: 승리 조건 체크

### 내부 메서드
- `_assign_roles(game)`: 역할 배정
- `_deal_initial_cards(game, card_manager)`: 초기 카드 분배

## 사용 예시

```python
from app.game.game_manager import GameManager

# 게임 매니저 생성
game_manager = GameManager()

# 게임 생성
game = game_manager.create_game()

# 플레이어 추가
game_manager.add_player_to_game(game.id, "player_1", "상인1")
game_manager.add_player_to_game(game.id, "player_2", "상인2")
game_manager.add_player_to_game(game.id, "player_3", "상인3")
game_manager.add_player_to_game(game.id, "player_4", "상인4")

# 게임 시작
game_manager.start_game(game.id)

# 게임 상태 조회
game_state = game_manager.get_game_state_dict(game.id, "player_1")

# 승리 조건 체크
win_info = game_manager.check_win_condition(game.id)
if win_info:
    print(f"승리자: {win_info['winner_id']}, 역할: {win_info['winner_role']}")
```

## 트러블슈팅

### 이슈: 역할 배정 시 상단주 위치
**문제**: 이전에는 상단주를 항상 첫 번째 플레이어에게 배정하여, 플레이어 순서와 역할이 강하게 연동되는 문제가 있었음

**해결**: 
- 상단주를 포함한 모든 역할을 한 번에 셔플
- 플레이어 순서(position)와 역할 배정을 분리하여, 어느 위치에도 상단주/적도 세력/야망가가 올 수 있도록 변경

**코드**:
```python
random.shuffle(roles)
final_roles = roles
```

### 이슈: 초기 재력 설정
**문제**: 역할 배정 후 초기 재력을 재설정해야 함

**해결**: 역할 배정 시 INITIAL_HP 상수를 사용하여 재력 재설정

**코드**:
```python
initial_hp = INITIAL_HP[final_roles[i]]
player.hp = initial_hp
player.max_hp = initial_hp
```

## 성능 고려사항

### 1. 게임 인스턴스 관리
- 딕셔너리 기반 조회: O(1) 시간 복잡도
- 게임 수가 많아지면 메모리 관리 필요

### 2. 승리 조건 체크
- 매 턴 종료 시 체크 (O(n) 시간 복잡도, n = 플레이어 수)
- 플레이어 수가 적어서 성능 문제 없음

### 3. 게임 상태 딕셔너리 변환
- Game 모델의 `to_dict()` 메서드 사용
- 플레이어 수에 비례하여 시간 소요
- WebSocket 전송 시 주기적으로 호출되므로 최적화 필요할 수 있음

### 4. 향후 개선 가능 사항
- 게임 히스토리 저장 (선택적)
- 게임 인스턴스 생명주기 관리 (장기 실행 시 메모리 누수 방지)
- 게임 수 제한 (필요시)

## 역할 배정 규칙

| 플레이어 수 | 역할 구성 |
|------------|----------|
| 4명 | 상단주 1, 원로원 1, 적도 세력 1, 야망가 1 |
| 5명 | 상단주 1, 원로원 1, 적도 세력 2, 야망가 1 |
| 6명 | 상단주 1, 원로원 2, 적도 세력 2, 야망가 1 |
| 7명 | 상단주 1, 원로원 2, 적도 세력 3, 야망가 1 |

## 초기 카드 분배

- 4명 이하: 플레이어당 4장
- 5명 이상: 플레이어당 5장

## 다음 단계
- [ ] 턴 관리자 구현 (TurnManager)
- [ ] 액션 핸들러 구현 (ActionHandler)
- [ ] WebSocket 통신 통합
- [ ] 게임 플로우 테스트

