# Python 개념 (초보자용)

이 프로젝트에서 사용하는 Python 개념을 초보자 수준으로 설명합니다.

---

## 1. async / await

### 이게 뭔가요?
`async`와 `await`는 **비동기 프로그래밍**을 위한 키워드입니다. 한 작업이 I/O(네트워크, 파일 등)를 기다리는 동안 다른 작업을 실행할 수 있어, 여러 클라이언트를 동시에 효율적으로 처리할 수 있습니다.

### 이 프로젝트에서 어떻게 쓰나요?
- WebSocket 연결 처리: `async def lobby_websocket_endpoint(...)`
- 메시지 수신 루프: `await websocket.receive_text()`
- 브로드캐스트: `await connection_manager.send_personal_message(...)`

### 예시
```python
async def handle_message(player_id: str, message: dict):
    result = await message_handler.handle_message(player_id, message)
    await connection_manager.broadcast(game_id, result)
```

---

## 2. 타입 힌트 (Type Hints)

### 이게 뭔가요?
변수, 함수 인자, 반환값에 **타입을 표기**하는 문법입니다. `str`, `int`, `Dict`, `Optional[T]` 등을 사용합니다. 코드 가독성과 IDE 자동완성, 버그 조기 발견에 도움이 됩니다.

### 이 프로젝트에서 어떻게 쓰나요?
- `app/models/`: Game, Player, Card 등 모든 모델
- `app/game/`: game_id: str, player_id: str
- `app/websocket/`: WebSocket, Dict 타입

### 예시
```python
def get_game(self, game_id: str) -> Optional[Game]:
    return self.games.get(game_id)
```

---

## 3. Enum

### 이게 뭔가요?
**고정된 상수 집합**을 타입으로 정의하는 클래스입니다. 역할(Role), 게임 상태(GameState), 카드 타입(CardType)처럼 제한된 값만 허용할 때 사용합니다.

### 이 프로젝트에서 어떻게 쓰나요?
- `app/utils/constants.py`: Role, GameState, TurnState, CardType, Suit, Rank

### 예시
```python
class Role(str, Enum):
    SHERIFF = "상단주"
    DEPUTY = "원로원"
    OUTLAW = "적도 세력"
    RENEGADE = "야망가"
```

---

## 4. 클래스와 인스턴스

### 이게 뭔가요?
**클래스**는 객체의 설계도이고, **인스턴스**는 그 설계도로 만든 실제 객체입니다. 상태(데이터)와 동작(메서드)을 묶어서 관리합니다.

### 이 프로젝트에서 어떻게 쓰나요?
- GameManager, ConnectionManager, MessageHandler: `main.py`에서 한 번 생성해 전역 사용
- Game, Player, Card: 게임 데이터를 담는 모델

### 예시
```python
game_manager = GameManager()
game_manager.create_game("game_1")
```

---

## 5. 딕셔너리 / set

### 이게 뭔가요?
- **딕셔너리(Dict)**: 키-값 쌍으로 데이터 저장. `{"game_1": game_object}`
- **set**: 중복 없는 집합. `{"player_1", "player_2"}`

### 이 프로젝트에서 어떻게 쓰나요?
- `GameManager.games: Dict[str, Game]` — 게임 ID → Game
- `ConnectionManager.active_connections: Dict[str, WebSocket]` — 플레이어 ID → WebSocket
- `ConnectionManager.game_players: Dict[str, Set[str]]` — 게임 ID → 플레이어 ID 집합

---

## 6. 모듈 / 패키지

### 이게 뭔가요?
- **모듈**: `.py` 파일 하나
- **패키지**: 여러 모듈을 담은 폴더 (`__init__.py` 포함)

### 이 프로젝트에서 어떻게 쓰나요?
- `app.game`, `app.models`, `app.websocket` 등으로 역할별 분리
- `from app.game.game_manager import GameManager`
