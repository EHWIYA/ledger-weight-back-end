# 모델 클래스 구현 문서

## 개요
게임의 핵심 데이터 구조를 나타내는 모델 클래스들의 구현 문서입니다.

## 구현된 모델

### 1. Role (역할)
**파일**: `app/models/role.py`

**의사결정 기록**:
- **선택한 방식**: Enum을 래핑한 클래스
- **이유**: 
  - Enum의 타입 안정성 유지
  - 역할별 편의 메서드 제공 (`is_sheriff`, `is_deputy` 등)
  - 향후 역할별 특수 능력 추가 용이

**코드 예시**:
```python
from app.models.role import Role
from app.utils.constants import Role as RoleEnum

# 역할 생성
role = Role(RoleEnum.SHERIFF)

# 역할 확인
if role.is_sheriff:
    print("상단주입니다")
```

**주요 메서드**:
- `is_sheriff()`, `is_deputy()`, `is_outlaw()`, `is_renegade()`: 역할 확인

---

### 2. Card (카드)
**파일**: `app/models/card.py`

**의사결정 기록**:
- **선택한 방식**: Pydantic BaseModel 사용
- **이유**:
  - 타입 검증 자동화
  - JSON 직렬화/역직렬화 용이
  - FastAPI와 자연스러운 통합
  - API 문서 자동 생성

**코드 예시**:
```python
from app.models.card import Card
from app.utils.constants import CardType, Suit, Rank

# 카드 생성
card = Card(
    id="bang_001",
    card_type=CardType.BANG,
    name="정산",
    suit=Suit.SPADES,
    rank=Rank.ACE,
    range=1,
    description="기본 공격 카드"
)

# 카드 타입 확인
if card.is_bang():
    print("정산 카드입니다")

# 공격 가능 여부 확인
can_attack = card.can_target(target_range=2)
```

**주요 메서드**:
- `is_bang()`, `is_missed()`, `is_beer()`: 카드 타입 확인
- `is_weapon()`, `is_equipment()`: 카드 분류 확인
- `can_target(target_range)`: 공격 가능 여부 확인
- `to_dict()`: 딕셔너리 변환 (WebSocket 전송용)

**트러블슈팅**:
- **이슈**: Enum 값의 JSON 직렬화 문제
- **해결**: `Config` 클래스에 `json_encoders` 설정 추가
- **결과**: Enum 값이 문자열로 올바르게 직렬화됨

---

### 3. Player (플레이어)
**파일**: `app/models/player.py`

**의사결정 기록**:
- **선택한 방식**: Pydantic BaseModel + 팩토리 메서드
- **이유**:
  - 역할별 초기 재력 자동 설정
  - 복잡한 초기화 로직 캡슐화
  - 타입 안정성 보장

**코드 예시**:
```python
from app.models.player import Player
from app.utils.constants import Role as RoleEnum

# 플레이어 생성
player = Player.create(
    player_id="player_1",
    name="상인1",
    role=RoleEnum.SHERIFF,
    position=0
)

# 피해 받기
died = player.take_damage(1)  # 재력 1 감소

# 재력 회복
player.heal(1)  # 재력 1 회복

# 카드 추가/제거
player.add_card(card)
removed_card = player.remove_card("card_id")

# 장착 카드
old_weapon = player.equip_card("weapon", weapon_card)

# 유효 영향력 계산
effective_range = player.get_effective_range()  # 무기 + 첩보원 적용
```

**주요 메서드**:
- `create()`: 팩토리 메서드로 플레이어 생성
- `take_damage(damage)`: 피해 받기 (사망 여부 반환)
- `heal(amount)`: 재력 회복
- `add_card(card)`, `remove_card(card_id)`: 핸드 카드 관리
- `equip_card(slot, card)`: 장착 카드 관리
- `get_effective_range()`: 유효 영향력 계산
- `to_dict(hide_hand)`: 딕셔너리 변환 (다른 플레이어는 핸드 숨김)

**성능 고려사항**:
- 핸드 카드는 리스트로 관리 (추가/제거 빈번)
- 장착 카드는 딕셔너리로 관리 (빠른 조회)
- `to_dict()` 시 `hide_hand` 옵션으로 불필요한 데이터 전송 방지

---

### 4. Game (게임)
**파일**: `app/models/game.py`

**의사결정 기록**:
- **선택한 방식**: 게임 상태를 중앙 집중식으로 관리
- **이유**:
  - 단일 진실의 원천 (Single Source of Truth)
  - 상태 일관성 보장
  - 게임 로직과 상태 분리

**코드 예시**:
```python
from app.models.game import Game
from app.models.player import Player
from app.utils.constants import GameState, TurnState

# 게임 생성
game = Game(id="game_001", state=GameState.WAITING)

# 플레이어 추가
player = Player.create("player_1", "상인1", RoleEnum.SHERIFF, 0)
game.add_player(player)

# 플레이어 조회
player = game.get_player("player_1")

# 거리 계산
distance = game.calculate_distance(player1, player2)

# 카드 뽑기
card = game.draw_card("player_1")

# 턴 관리
game.set_current_player("player_1")
game.set_turn_state(TurnState.PLAY_CARD)
```

**주요 메서드**:
- `add_player(player)`, `remove_player(player_id)`: 플레이어 관리
- `get_player(player_id)`: 플레이어 조회
- `get_alive_players()`: 생존 플레이어 목록
- `calculate_distance(from_player, to_player)`: 거리 계산
- `draw_card(player_id)`: 카드 뽑기
- `discard_card(card)`: 카드 버리기
- `get_next_player(current_player_id)`: 다음 플레이어 조회
- `to_dict(player_id)`: 게임 상태 딕셔너리 변환

**트러블슈팅**:
- **이슈**: 원형 구조에서 거리 계산 복잡성
- **해결**: 양방향 거리 계산 후 최소값 선택
- **결과**: 플레이어 위치가 원형이어도 정확한 거리 계산

**성능 고려사항**:
- 플레이어 조회는 O(n) - 플레이어 수가 적어서 허용
- 덱은 리스트로 관리 (앞에서 뽑기)
- 버림 더미는 리스트로 관리 (뒤에 추가)
- 향후 플레이어 수가 많아지면 딕셔너리로 최적화 가능

---

## 모델 간 관계

```
Game
├── players: List[Player]
│   ├── role: Role
│   ├── hand: List[Card]
│   └── equipment: Dict[str, Card]
├── deck: List[Card]
└── discard_pile: List[Card]
```

## 데이터 흐름

1. **게임 생성** → `Game` 인스턴스 생성
2. **플레이어 추가** → `Player` 생성 후 `Game.add_player()`
3. **카드 뽑기** → `Game.draw_card()` → `Player.add_card()`
4. **카드 사용** → `Player.remove_card()` → `Game.discard_card()`
5. **상태 전송** → `Game.to_dict()` → WebSocket 브로드캐스트

## 다음 단계
- [ ] 카드 덱 생성 로직 구현 (`CardManager`)
- [ ] 게임 초기화 로직 구현 (`GameManager`)
- [ ] 모델 단위 테스트 작성

