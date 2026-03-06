# WebSocket 구현 문서

## 개요
WebSocket 기반 실시간 통신을 구현한 문서입니다. ConnectionManager와 MessageHandler를 통해 게임 상태를 실시간으로 동기화합니다.

## 구현 내용

### 파일
- `app/websocket/connection_manager.py` - ConnectionManager 클래스
- `app/websocket/message_handler.py` - MessageHandler 클래스
- `app/main.py` - WebSocket 엔드포인트

## 의사결정 기록

### 1. 연결 관리 방식
**선택한 방식**: 플레이어 ID 기반 연결 관리 + 게임별 플레이어 그룹핑

**이유**:
- 플레이어별 개별 메시지 전송 가능
- 게임별 브로드캐스트 용이
- 연결 해제 시 자동 정리

**코드 예시**:
```python
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}  # 플레이어 ID -> WebSocket
        self.game_players: Dict[str, Set[str]] = {}  # 게임 ID -> 플레이어 ID 집합
        self.player_games: Dict[str, str] = {}  # 플레이어 ID -> 게임 ID
```

### 2. 메시지 처리 방식
**선택한 방식**: 메시지 타입별 핸들러 메서드 분리

**이유**:
- 명확한 책임 분리
- 확장 용이
- 디버깅 용이

**코드 예시**:
```python
async def handle_message(self, player_id: str, message: dict) -> Dict:
    message_type = message.get("type")
    
    if message_type == "PLAYER_ACTION":
        return await self.handle_player_action(player_id, message)
    elif message_type == "JOIN_GAME":
        return await self.handle_join_game(player_id, message)
```

### 3. 게임 상태 동기화
**선택한 방식**: 액션 처리 후 자동 브로드캐스트

**이유**:
- 모든 플레이어가 동일한 상태 유지
- 실시간 동기화 보장
- 수동 업데이트 불필요

**코드 예시**:
```python
# 액션 처리 후
result = action_handler.handle_action(action_type, player_id, data)

if result.get("success"):
    await self.broadcast_game_state(game_id)  # 자동 브로드캐스트
```

### 4. 전역 인스턴스 사용
**선택한 방식**: main.py에서 전역 인스턴스 생성

**이유**:
- FastAPI 앱 생명주기와 일치
- 모든 요청에서 동일한 인스턴스 사용
- 간단한 구조

**코드 예시**:
```python
# 전역 인스턴스
game_manager = GameManager()
connection_manager = ConnectionManager()
message_handler = MessageHandler(game_manager, connection_manager)
```

## 주요 메서드

### ConnectionManager
- `connect(websocket, player_id)`: WebSocket 연결 수락 및 등록
- `disconnect(player_id)`: 연결 해제
- `register_player_to_game(player_id, game_id)`: 플레이어를 게임에 등록
- `send_personal_message(message, player_id)`: 개별 메시지 전송
- `broadcast_to_game(message, game_id)`: 게임 전체 브로드캐스트
- `broadcast_to_all(message)`: 모든 연결 브로드캐스트

### MessageHandler
- `handle_message(player_id, message)`: 메시지 처리 (메인 진입점)
- `handle_player_action(player_id, message)`: 플레이어 액션 처리
- `handle_join_game(player_id, message)`: 게임 참여 처리
- `handle_get_game_state(player_id, message)`: 게임 상태 조회
- `send_game_state_to_player(player_id, game_id)`: 개별 게임 상태 전송
- `broadcast_game_state(game_id)`: 게임 상태 브로드캐스트
- `broadcast_win_info(game_id, win_info)`: 승리 정보 브로드캐스트

## 메시지 프로토콜

### 클라이언트 → 서버

#### 1. JOIN_GAME
```json
{
  "type": "JOIN_GAME",
  "game_id": "game_123",
  "player_name": "상인1"
}
```

#### 2. PLAYER_ACTION
```json
{
  "type": "PLAYER_ACTION",
  "action": {
    "type": "USE_CARD",
    "cardId": "bang_001",
    "targetId": "player_2"
  }
}
```

#### 3. GET_GAME_STATE
```json
{
  "type": "GET_GAME_STATE"
}
```

#### 4. START_GAME
```json
{
  "type": "START_GAME",
  "game_id": "game_123"
}
```

- `game_id`는 선택(optional) 값입니다. 생략 시, 현재 WebSocket 연결이 속한 게임 ID를 서버가 자동으로 사용합니다.
- 게임 상태가 `WAITING`이고, 총 플레이어 수(인간 + 봇)가 최소 인원 이상일 때만 게임이 시작됩니다.

#### 5. ADD_AI_PLAYER
```json
{
  "type": "ADD_AI_PLAYER",
  "game_id": "game_123",
  "count": 3,
  "difficulty": "medium"
}
```

- `game_id`는 선택 값이며, 생략 시 현재 플레이어가 속한 게임에 AI가 추가됩니다.
- `count`는 1 이상의 정수여야 하며, 한 번의 요청으로는 최대 `MAX_PLAYERS`까지 요청할 수 있습니다. 실제로는 남은 슬롯 수(`MAX_PLAYERS - 현재 인원`)만큼만 추가되며, 응답의 `added_count` 필드로 실제 추가 인원을 확인할 수 있습니다.
- `difficulty`는 `"easy"`, `"medium"`, `"hard"` 중 하나여야 합니다. 현재 버전에서는 주로 AI 이름/이벤트 로그에만 영향을 주며, 행동 로직 차이는 점진적으로 확장할 예정입니다.
- 최소/최대 인원은 `app/utils/constants.py`의 `MIN_PLAYERS`(기본 4), `MAX_PLAYERS`(기본 7)로 정의되어 있으며, **인간 + 봇을 모두 포함한 총 플레이어 수** 기준으로 판단합니다.

#### 6. PING (하트비트)
```json
{
  "type": "PING"
}
```

- 클라이언트는 `WS_HEARTBEAT_INTERVAL`(기본 30초) 이하 주기로 `PING` 메시지를 전송하여 연결이 여전히 유효한지 서버와 상호 확인합니다.
- 서버는 각 `PING`에 대해 `PONG` 메시지로 응답합니다.

### 서버 → 클라이언트

#### 1. CONNECTION_ESTABLISHED
```json
{
  "type": "CONNECTION_ESTABLISHED",
  "message": "연결이 성공적으로 설정되었습니다.",
  "player_id": "player_1"
}
```

#### 2. GAME_STATE_UPDATE
```json
{
  "type": "GAME_STATE_UPDATE",
  "gameId": "game_123",
  "players": [
    {
      "id": "player_001",
      "name": "홍길동",
      "hp": 4,
      "wealth": 4,
      "influence": 1,
      "role": "상단주",           // 자신의 역할만 표시, 다른 플레이어는 null
      "hand": [                  // 자신의 핸드는 전체 카드, 다른 플레이어는 빈 배열
        {
          "id": "card_001",
          "name": "정산",
          "type": "BANG"
        }
      ],
      "handCount": 2,
      "tableCards": [],
      "treasures": [],
      "isAlive": true,
      "position": 0,
      "isBot": false
    }
  ],
  "currentTurn": "player_001",
  "turnState": {
    "currentTurn": "player_001",
    "timeLeft": 60,
    "requiredResponse": {       // optional, 대응 단계일 때만
      "type": "RESPOND_ATTACK",
      "message": "홍길동이(가) 공격을 받았습니다. 회피하시겠습니까?"
    }
  },
  "events": [
    {
      "id": "event_001",
      "timestamp": 1702387200000,
      "message": "게임이 시작되었습니다!",
      "type": "notification"
    }
  ],
  "phase": "lobby"              // "lobby" | "playing" | "finished"
}
```

#### 3. ACTION_RESPONSE
```json
{
  "type": "ACTION_RESPONSE",
  "data": {
    "success": true,
    "message": "정산 카드를 사용했습니다.",
    "event": "플레이어 1이 정산 카드를 사용했습니다."
  }
}
```

- 에러가 발생한 경우 `data.success`가 `false`가 되며, `data.error_code` 필드에 기계가 읽을 수 있는 에러 코드(예: `"GAME_NOT_FOUND"`, `"PLAYER_NOT_IN_GAME"`, `"INVALID_JSON"` 등)가 함께 포함됩니다.

#### 4. GAME_END
```json
{
  "type": "GAME_END",
  "data": {
    "winner_id": "player_1",
    "winner_role": "상단주",
    "reason": "상단주 팀이 승리했습니다."
  }
}
```

#### 5. PONG (하트비트 응답)
```json
{
  "type": "PONG",
  "timestamp": "2026-03-05T12:34:56.789123+00:00"
}
```

- 서버는 클라이언트로부터 `PING` 메시지를 수신할 때마다 현재 UTC 시간 기준 ISO8601 문자열을 `timestamp`로 포함한 `PONG` 메시지를 전송합니다.

#### 6. ERROR
```json
{
  "type": "ERROR",
  "code": "INVALID_JSON",
  "message": "잘못된 JSON 형식입니다."
}
```

- JSON 파싱 오류, 인증 실패, 게임 참가 실패 등 WebSocket 레벨의 에러는 `type: "ERROR"` 형식으로 전달됩니다.
- `code` 필드는 클라이언트에서 분기 처리를 위한 에러 코드이며, `message`는 사용자 표시용 한글 메시지입니다.

## 사용 예시

### 서버 시작
```python
# app/main.py에서 자동으로 WebSocket 엔드포인트 생성
# ws://localhost:8000/ws/{player_id}
```

### 클라이언트 연결
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/player_1');

ws.onmessage = (event) => {
  const message = JSON.parse(event.data);
  
  if (message.type === 'GAME_STATE_UPDATE') {
    // 게임 상태 업데이트
    updateGameState(message.data);
  }
};

// 게임 참여
ws.send(JSON.stringify({
  type: 'JOIN_GAME',
  game_id: 'game_123',
  player_name: '상인1'
}));

// 카드 사용
ws.send(JSON.stringify({
  type: 'PLAYER_ACTION',
  action_type: 'USE_CARD',
  data: {
    card_id: 'bang_001',
    target_id: 'player_2'
  }
}));
```

## 트러블슈팅

### 이슈: 연결 해제 감지
**문제**: 클라이언트가 연결을 끊었을 때 감지 및 정리 필요

**해결**: 
- `WebSocketDisconnect` 예외 처리
- `finally` 블록에서 연결 해제 처리
- 게임에서 플레이어 자동 제거

**코드**:
```python
try:
    while True:
        data = await websocket.receive_text()
        # 메시지 처리...
except WebSocketDisconnect:
    pass
finally:
    connection_manager.disconnect(player_id)
```

### 이슈: JSON 파싱 에러
**문제**: 잘못된 JSON 형식 메시지 처리

**해결**: 
- `json.JSONDecodeError` 예외 처리
- 에러 메시지 전송 (`type: "ERROR"`, `code: "INVALID_JSON"`)

**코드**:
```python
try:
    message = json.loads(data)
except json.JSONDecodeError:
    await connection_manager.send_personal_message(
        {
            "type": "ERROR",
            "code": "INVALID_JSON",
            "message": "잘못된 JSON 형식입니다.",
        },
        player_id,
    )
```

### 이슈: 게임 상태 동기화
**문제**: 모든 플레이어가 동일한 게임 상태를 봐야 함

**해결**: 
- 액션 처리 후 자동 브로드캐스트
- 각 플레이어에게 맞는 상태 전송 (핸드 카드 숨김)

**코드**:
```python
# 각 플레이어에게 맞는 상태 전송
game_state = self.game_manager.get_game_state_dict(game_id, player_id)
# player_id가 None이면 자신의 핸드는 보이고, 다른 플레이어는 숨김
```

## 성능 고려사항

### 1. 연결 관리 최적화
- 딕셔너리 기반 조회: O(1) 시간 복잡도
- 연결 수 제한: `WS_MAX_CONNECTIONS` 설정

### 2. 브로드캐스트 최적화
- 게임별 그룹 브로드캐스트: 필요한 플레이어에게만 전송
- 개별 메시지 전송 실패 시 자동 정리

### 3. 메시지 처리 최적화
- 비동기 처리: `async/await` 사용
- 메시지 타입별 분기 처리

### 4. 향후 개선 가능 사항
- 하트비트 주기 및 타임아웃 튜닝 (데드 연결 감지 민감도 조정)
- 메시지 큐 (연결 끊김 시 재전송)
- 압축 (대용량 메시지)

## 보안 고려사항

### 현재 구현
- 플레이어 ID 기반 인증 (기본)
- 연결 수 제한
- WebSocket 쿼리 파라미터 기반 토큰 훅 (`token` 파라미터, `app/security/auth.py`) — 현재는 토큰 문자열을 그대로 `player_id`로 사용하며, 이후 JWT 디코딩 로직으로 교체 예정

### 향후 개선 필요
- JWT 토큰 기반 인증 (`app/security/auth.py`의 `get_player_id_from_token` 구현 교체)
- 플레이어 ID 검증
- Rate Limiting
- 메시지 크기 제한

## 다음 단계
- [ ] 프론트엔드와 연결 테스트
- [x] 하트비트 메커니즘 구현
- [x] 인증 시스템 추가 (토큰 훅 및 확장 포인트)
- [x] 에러 처리 강화 (에러 코드 표준화 및 ERROR 메시지 타입 추가)

