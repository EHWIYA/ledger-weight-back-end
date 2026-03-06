# WebSocket 개념 (초보자용)

WebSocket은 **양방향 실시간 통신** 프로토콜입니다. 이 프로젝트의 핵심 통신 방식입니다.

---

## 1. WebSocket이란?

### 이게 뭔가요?
HTTP처럼 요청-응답을 반복하는 것이 아니라, **한 번 연결을 맺으면** 서버와 클라이언트가 **계속 메시지를 주고받을 수 있는** 프로토콜입니다. 게임, 채팅, 실시간 알림에 적합합니다.

### HTTP vs WebSocket
- **HTTP**: 클라이언트 요청 → 서버 응답 → 연결 종료
- **WebSocket**: 연결 유지 → 양방향 메시지 교환

---

## 2. 이 프로젝트의 WebSocket 흐름

1. **연결**: 클라이언트가 `ws://.../lobby/{game_id}?player=이름` 접속
2. **수락**: 서버가 `accept()` 후 `CONNECTION_ESTABLISHED` 전송
3. **참가**: 자동으로 `JOIN_GAME` 처리, `GAME_STATE_UPDATE` 전송
4. **메시지 루프**: 클라이언트 메시지 수신 → `MessageHandler` 처리 → 응답/브로드캐스트
5. **종료**: 연결 해제 시 `disconnect()` 호출

---

## 3. 메시지 타입 (클라이언트 → 서버)

| 타입 | 설명 |
|------|------|
| START_GAME | 게임 시작 요청 |
| PLAYER_ACTION | 카드 사용, 턴 종료, 공격 대응 |
| GET_GAME_STATE | 게임 상태 조회 |
| ADD_AI_PLAYER | AI 플레이어 추가 |
| PING | 연결 유지용 (서버가 PONG 응답) |

---

## 4. 메시지 타입 (서버 → 클라이언트)

| 타입 | 설명 |
|------|------|
| GAME_STATE_UPDATE | 게임 상태 전체 |
| CONNECTION_ESTABLISHED | 연결 성공 (player_id 포함) |
| ACTION_RESPONSE | 액션 처리 결과 |
| ERROR | 에러 메시지 |
| PONG | PING에 대한 응답 |

---

## 5. 관련 파일

- `app/main.py` — WebSocket 엔드포인트
- `app/websocket/connection_manager.py` — 연결 관리
- `app/websocket/message_handler.py` — 메시지 타입별 처리
