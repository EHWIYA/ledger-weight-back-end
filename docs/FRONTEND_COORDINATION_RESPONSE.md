# 프론트엔드 연동 준비 완료 보고서

**작성일**: 2025-12-12  
**작성자**: 백엔드 개발자  
**대상**: 프론트엔드 담당자

---

## 📋 개요

프론트엔드 연동을 위한 주요 기능 구현이 완료되어, 이제 연동 테스트를 진행할 수 있는 상태입니다.  
이 문서는 구현 완료된 기능과 연동 방법을 안내합니다.

---

## ✅ 구현 완료된 기능

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

---

## 🔌 WebSocket 엔드포인트 정보

### 로비 연결 엔드포인트

**URL 형식**:
```
ws://localhost:8080/lobby/{game_id}?player={playerName}
```

**예시**:
```
ws://localhost:8080/lobby/game_12345?player=홍길동
```

**동작**:
1. 연결 시 서버에서 플레이어 ID (UUID) 자동 생성
2. `CONNECTION_ESTABLISHED` 메시지 수신 (플레이어 ID 포함)
3. 자동으로 게임 참가 처리
4. `GAME_STATE_UPDATE` 메시지 자동 수신

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

## 📨 메시지 프로토콜

### 클라이언트 → 서버 메시지

#### 1. 게임 시작 요청
```json
{
  "type": "START_GAME",
  "game_id": "game_12345"  // optional, 없으면 플레이어가 속한 게임 사용
}
```

**응답**:
- 성공: `ACTION_RESPONSE` 메시지 + `GAME_STATE_UPDATE` 브로드캐스트
- 실패: `ACTION_RESPONSE` 메시지 (에러 메시지 포함)

#### 2. 플레이어 액션
```json
{
  "type": "PLAYER_ACTION",
  "action": {
    "type": "USE_CARD",
    "cardId": "card_001",
    "targetId": "player_002"  // optional
  }
}
```

**액션 타입**:
- `USE_CARD`: 카드 사용
- `END_TURN`: 턴 종료
- `RESPOND_ATTACK`: 공격 대응
  ```json
  {
    "type": "PLAYER_ACTION",
    "action": {
      "type": "RESPOND_ATTACK",
      "response": "evade",  // "evade" | "give_up"
      "cardId": "card_001"  // "evade"일 때만 필요
    }
  }
  ```

#### 3. 게임 상태 조회
```json
{
  "type": "GET_GAME_STATE"
}
```

### 서버 → 클라이언트 메시지

#### 1. 게임 상태 업데이트
```json
{
  "type": "GAME_STATE_UPDATE",
  "gameId": "game_12345",
  "players": [
    {
      "id": "player_001",
      "name": "홍길동",
      "hp": 4,
      "wealth": 4,
      "influence": 0,
      "role": "상단주",  // 자신의 역할만 표시, 다른 플레이어는 null
      "hand": [  // 자신의 핸드는 전체 카드, 다른 플레이어는 null
        {
          "id": "card_001",
          "name": "뱅!",
          "type": "BANG"
        }
      ],
      "handCount": 2,  // 다른 플레이어의 핸드 개수
      "tableCards": [],
      "treasures": [],
      "isAlive": true,
      "position": 0
    }
  ],
  "currentTurn": "player_001",
  "turnState": {
    "currentTurn": "player_001",
    "timeLeft": 60,  // TODO: 실제 타이머 구현 예정
    "requiredResponse": {  // optional, 대응 단계일 때만
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
  "phase": "lobby"  // "lobby" | "playing" | "finished"
}
```

#### 2. 에러 메시지
```json
{
  "type": "ERROR",
  "message": "게임을 시작하려면 최소 4명의 플레이어가 필요합니다. (현재: 2명)"
}
```

#### 3. 액션 응답
```json
{
  "type": "ACTION_RESPONSE",
  "data": {
    "success": true,
    "message": "게임이 시작되었습니다.",
    "game_id": "game_12345"
  }
}
```

---

## 🧪 연동 테스트 방법

### 1. 기본 연결 테스트

```javascript
const gameId = "test_game_001";
const playerName = "테스트플레이어";
const ws = new WebSocket(`ws://localhost:8080/lobby/${gameId}?player=${encodeURIComponent(playerName)}`);

ws.onopen = () => {
  console.log("WebSocket 연결 성공");
};

ws.onmessage = (event) => {
  const message = JSON.parse(event.data);
  console.log("수신 메시지:", message);
  
  switch (message.type) {
    case "CONNECTION_ESTABLISHED":
      console.log("플레이어 ID:", message.player_id);
      break;
    case "GAME_STATE_UPDATE":
      console.log("게임 상태:", message);
      break;
    case "ERROR":
      console.error("에러:", message.message);
      break;
  }
};

ws.onerror = (error) => {
  console.error("WebSocket 에러:", error);
};

ws.onclose = () => {
  console.log("WebSocket 연결 종료");
};
```

### 2. 게임 시작 테스트

```javascript
// 최소 4명의 플레이어가 연결된 후
ws.send(JSON.stringify({
  type: "START_GAME",
  game_id: "test_game_001"
}));
```

### 3. 플레이어 액션 테스트

```javascript
// 카드 사용
ws.send(JSON.stringify({
  type: "PLAYER_ACTION",
  action: {
    type: "USE_CARD",
    cardId: "card_001",
    targetId: "player_002"
  }
}));

// 턴 종료
ws.send(JSON.stringify({
  type: "PLAYER_ACTION",
  action: {
    type: "END_TURN"
  }
}));
```

---

## 🌐 서버 접속 정보

### 개발 환경 (로컬)
- **URL**: `ws://localhost:8080` 또는 `ws://192.168.0.10:8080`
- **HTTP**: `http://localhost:8080` 또는 `http://192.168.0.10:8080`
- **API 문서**: `http://localhost:8080/docs`

**⚠️ 중요**: 
- 로컬 서버 실행이 필요합니다. 아래 "서버 실행 방법"을 참고하세요.
- **`10.0.2.2`는 사용할 수 없습니다**. 이 IP는 Android 에뮬레이터 전용이며, 현재 서버 IP가 아닙니다.
- **올바른 IP**: `192.168.0.10` (로컬 네트워크) 또는 `localhost` (같은 머신)
- 자세한 내용은 `docs/WEBSOCKET_CONNECTION_TROUBLESHOOTING.md` 참고

### 프로덕션 환경
- **URL**: `wss://ledger-weight-api.livbee.co.kr`
- **HTTP**: `https://ledger-weight-api.livbee.co.kr`
- **API 문서**: `https://ledger-weight-api.livbee.co.kr/docs`

**현재 상태**: 프로덕션 서버는 배포 완료되어 사용 가능합니다.

---

## 🖥️ 서버 실행 방법 (로컬 개발 환경)

### 사전 준비
1. **Python 3.8 이상 설치 확인**
   ```bash
   python --version
   ```

2. **의존성 설치**
   ```bash
   cd ledger-weight-back-end
   pip install -r requirements.txt
   ```

3. **환경 변수 설정** (선택사항)
   - `.env` 파일이 있다면 설정 확인
   - 없어도 기본값으로 동작합니다

### 서버 실행

**방법 1: 개발 모드 (권장)**
```bash
cd ledger-weight-back-end
uvicorn app.main:app --reload --host 0.0.0.0 --port 8080
```

**방법 2: 프로덕션 모드**
```bash
cd ledger-weight-back-end
uvicorn app.main:app --host 0.0.0.0 --port 8080
```

**방법 3: Python 모듈로 실행**
```bash
cd ledger-weight-back-end
python -m uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload
```

### 서버 실행 확인

서버가 정상적으로 실행되면 다음 URL에서 확인할 수 있습니다:
- **헬스 체크**: `http://localhost:8080/health`
- **API 문서**: `http://localhost:8080/docs`
- **서버 정보**: `http://localhost:8080/`

**예상 응답**:
```json
{
  "status": "healthy"
}
```

### 서버 실행 중 문제 해결

1. **포트 8080이 이미 사용 중인 경우**
   - 다른 포트 사용: `--port 8081`
   - 또는 기존 프로세스 종료

2. **의존성 오류**
   ```bash
   pip install --upgrade -r requirements.txt
   ```

3. **모듈을 찾을 수 없는 경우**
   - 프로젝트 루트 디렉토리에서 실행 확인
   - Python 경로 확인

### 서버 중지
- 터미널에서 `Ctrl + C`로 중지

---

## ⚠️ 주의사항 및 제한사항

### 1. 게임 시작 조건
- 최소 플레이어 수: **4명**
- 최대 플레이어 수: **7명**
- 게임 상태가 `WAITING`일 때만 시작 가능

### 2. 플레이어 ID 관리
- 플레이어 ID는 서버에서 자동 생성 (UUID)
- 로비 연결 시 `CONNECTION_ESTABLISHED` 메시지에서 `player_id` 수신
- 이후 메시지 전송 시 `player_id`는 필요 없음 (연결 정보로 자동 식별)

### 3. 게임 상태 Phase
- `lobby`: 게임 시작 전 대기 상태
- `playing`: 게임 진행 중
- `finished`: 게임 종료

### 4. 핸드 카드 정보
- 자신의 핸드: 전체 카드 정보 배열
- 다른 플레이어의 핸드: `null` (개수는 `handCount`로 확인)

### 5. 역할 정보
- 자신의 역할: 역할 이름 문자열 (예: "상단주", "부하", "무법자", "배신자")
- 다른 플레이어의 역할: `null` (게임 시작 전까지)

### 6. 재력 및 영향력 필드
- `wealth`: 항상 정수(`number`)로 내려가는 재력 표시용 필드입니다. 현재는 내부 체력(`hp`) 값과 동일하게 내려갑니다.
- `influence`: 항상 정수(`number`)로 내려가는 영향력(사거리) 필드입니다. 장착 카드/보물 효과가 반영된 최종 값이며, `null` 이나 누락 상태로 내려가지 않습니다.

---

## 🔄 다음 단계 및 협의 사항

### 즉시 테스트 가능
1. ✅ 로비 연결 및 게임 참가
2. ✅ 게임 시작 프로토콜
3. ✅ 게임 상태 조회
4. ✅ 기본 플레이어 액션 (카드 사용, 턴 종료)

### 추가 구현 예정 (우선순위 순)
1. **턴 타이머**: 서버 측 타이머 관리 및 `timeLeft` 업데이트
2. **에러 코드 체계**: 표준화된 에러 코드 정의
3. **타겟팅 검증 강화**: 영향력 범위 검증 로직 개선
4. **게임 진행 중 재연결**: `/game/{game_id}` 엔드포인트 (선택사항)

### 협의 필요 사항
1. **턴 타이머 동작 방식**
   - 서버에서 타이머 관리 vs 클라이언트에서 타이머 관리
   - 타이머 만료 시 자동 처리 방식

2. **에러 코드 체계**
   - 에러 코드 형식 및 목록 협의
   - 에러 메시지 다국어 지원 여부

3. **게임 이벤트 로그**
   - 이벤트 메시지 형식 및 내용 협의
   - 이벤트 필터링 옵션 필요 여부

---

## 📞 문의 및 피드백

연동 테스트 중 문제가 발생하거나 추가 기능이 필요한 경우, 언제든지 문의해주세요.

**연락 방법**:
- 이슈 트래커: GitHub Issues
- 이메일: [이메일 주소]
- 슬랙/디스코드: [채널 정보]

---

## 📝 변경 이력

- **2025-12-12**: 
  - 로비 엔드포인트 및 게임 시작 프로토콜 구현 완료
  - AI 플레이어 추가 기능 구현 완료 (`ADD_AI_PLAYER` 메시지 처리)
  - 프론트엔드 연동 준비 문서 작성 완료
  - WebSocket 연결 문제 해결 가이드 작성
  - 서버 실행 스크립트 생성
- **2025-12-11**: 메시지 프로토콜 표준화 완료

---

**작성자**: 백엔드 개발자  
**최종 업데이트**: 2025-12-12

