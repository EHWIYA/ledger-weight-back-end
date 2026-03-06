# 프론트엔드 연동 가이드

**작성일**: 2025-12-11  
**최종 업데이트**: 2025-12-12  
**상태**: 진행 중

---

## 개요

프론트엔드 담당자와의 공조 메일을 바탕으로 WebSocket 프로토콜 및 API 연동을 위한 작업 계획과 구현 현황을 정리한 문서입니다.

---

## 구현 완료된 기능

### 1. 로비 WebSocket 엔드포인트
- **엔드포인트**: `/lobby/{game_id}?player={playerName}`
- **기능**:
  - 플레이어 이름을 쿼리 파라미터로 받음
  - 서버에서 UUID 기반 플레이어 ID 자동 생성
  - 연결 성공 시 자동으로 게임 참가 처리
  - `CONNECTION_ESTABLISHED` 메시지 전송 (플레이어 ID 포함)
  - `GAME_STATE_UPDATE` 메시지 자동 전송

### 2. 게임 시작 프로토콜
- **메시지 타입**: `START_GAME`
- **기능**:
  - 최소 플레이어 수 확인 (4명 이상)
  - 게임 상태 검증 (WAITING 상태만 시작 가능)
  - 역할 배정 및 초기화
  - 게임 시작 이벤트 로그 추가
  - 모든 플레이어에게 게임 상태 브로드캐스트

### 3. 메시지 프로토콜 표준화
- **클라이언트 → 서버**: `PLAYER_ACTION` 메시지 형식 프론트엔드 요청 형식으로 변경 완료
- **서버 → 클라이언트**: `GAME_STATE_UPDATE` 메시지 형식 프론트엔드 요청 형식으로 변경 완료
- **게임 이벤트 로그**: 최근 50개 이벤트 포함 (타입: `action`, `notification`, `error`)

### 4. AI 플레이어 추가
- **메시지 타입**: `ADD_AI_PLAYER`
- **기능**: 난이도별 AI 플레이어 추가, 최대 7명까지

---

## WebSocket 엔드포인트 정보

### 로비 연결
```
ws://localhost:8088/lobby/{game_id}?player={playerName}
```

**연결 성공 메시지**:
```json
{
  "type": "CONNECTION_ESTABLISHED",
  "message": "로비에 연결되었습니다.",
  "player_id": "550e8400-e29b-41d4-a716-446655440000",
  "player_name": "홍길동",
  "game_id": "game_12345"
}
```

---

## 메시지 프로토콜

### 클라이언트 → 서버

| 메시지 타입 | 설명 |
|------------|------|
| `START_GAME` | 게임 시작 요청 |
| `PLAYER_ACTION` | 카드 사용, 턴 종료, 공격 대응 |
| `GET_GAME_STATE` | 게임 상태 조회 |
| `ADD_AI_PLAYER` | AI 플레이어 추가 |

### 서버 → 클라이언트

| 메시지 타입 | 설명 |
|------------|------|
| `GAME_STATE_UPDATE` | 게임 상태 전체 업데이트 |
| `ERROR` | 에러 메시지 |
| `ACTION_RESPONSE` | 액션 처리 결과 |

---

## 서버 접속 정보

- **개발**: `ws://localhost:8088` (또는 `http://localhost:8088`)
- **프로덕션**: `wss://ledger-weight-api.livbee.co.kr`
- **API 문서**: `/docs` (Swagger UI)

---

## 추가 구현 예정

1. **턴 타이머**: 서버 측 타이머 관리 및 `timeLeft` 업데이트
2. **에러 코드 체계**: 표준화된 에러 코드 정의
3. **타겟팅 검증 강화**: 영향력 범위 검증 로직 개선

---

## 관련 문서

- [WebSocket 트러블슈팅](websocket-troubleshooting.md)
- [프로젝트 개요](../project/overview.md)
