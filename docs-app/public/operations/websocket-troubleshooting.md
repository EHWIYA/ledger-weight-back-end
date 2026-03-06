# WebSocket 연결 문제 해결 가이드

**작성일**: 2025-12-12  
**대상**: 프론트엔드 개발자

---

## 🔍 문제 진단 결과

### 서버 상태 확인
- ✅ **서버 실행 중**: `0.0.0.0:8080`에서 리스닝 중
- ✅ **헬스 체크**: `http://localhost:8080/health` 정상 응답
- ✅ **WebSocket 엔드포인트**: `/lobby/{game_id}` 정상 작동

### 네트워크 확인
- **현재 서버 IP 주소**:
  - Tailscale IP: `100.71.130.16`
  - 로컬 네트워크 IP: `192.168.0.10`
- **요청된 IP**: `10.0.2.2` ❌ (연결 실패)

---

## ⚠️ 문제 원인

`10.0.2.2`는 **Android 에뮬레이터나 가상 머신**에서 호스트 머신을 가리키는 특수 IP 주소입니다.

**현재 상황**:
- 서버는 실제 물리 머신에서 실행 중
- `10.0.2.2`는 현재 서버의 IP가 아님
- 따라서 연결이 실패함

---

## ✅ 해결 방법

### 방법 1: 로컬 네트워크 IP 사용 (권장)

프론트엔드 코드에서 다음 IP 중 하나를 사용하세요:

```javascript
// 옵션 1: 로컬 네트워크 IP (같은 네트워크 내에서 접근 가능)
const ws = new WebSocket(`ws://192.168.0.10:8080/lobby/${gameId}?player=${playerName}`);

// 옵션 2: localhost (같은 머신에서 실행 시)
const ws = new WebSocket(`ws://localhost:8080/lobby/${gameId}?player=${playerName}`);

// 옵션 3: 127.0.0.1 (같은 머신에서 실행 시)
const ws = new WebSocket(`ws://127.0.0.1:8080/lobby/${gameId}?player=${playerName}`);
```

### 방법 2: Android 에뮬레이터에서 접근하는 경우

**Android 에뮬레이터**에서 호스트에 접근하려면:
- `10.0.2.2`는 에뮬레이터의 특수 IP (호스트를 가리킴)
- 하지만 **서버가 실제 물리 머신에서 실행 중**이므로 에뮬레이터에서 직접 접근 불가

**해결책**:
1. **같은 네트워크에서 접근**: 에뮬레이터와 서버가 같은 Wi-Fi 네트워크에 있어야 함
2. **로컬 네트워크 IP 사용**: `192.168.0.10:8080` 사용
3. **포트 포워딩**: ADB 포트 포워딩 사용 (복잡함)

### 방법 3: 환경 변수로 IP 관리

프론트엔드에서 환경 변수로 서버 주소를 관리하세요:

```javascript
// .env 또는 환경 설정
const API_BASE_URL = process.env.REACT_APP_API_URL || 'ws://localhost:8080';
// 또는
const API_BASE_URL = process.env.REACT_APP_API_URL || 'ws://192.168.0.10:8080';

const ws = new WebSocket(`${API_BASE_URL}/lobby/${gameId}?player=${playerName}`);
```

---

## 🔌 올바른 WebSocket 연결 URL 형식

### 기본 형식
```
ws://[서버_IP]:8080/lobby/{game_id}?player={playerName}
```

### 예시
```javascript
// 게임 ID와 플레이어 이름
const gameId = "test_game_001";
const playerName = "홍길동";

// 올바른 연결 방법
const ws = new WebSocket(
  `ws://192.168.0.10:8080/lobby/${gameId}?player=${encodeURIComponent(playerName)}`
);
```

---

## 🧪 연결 테스트 방법

### 1. 브라우저 콘솔에서 테스트

```javascript
const ws = new WebSocket('ws://192.168.0.10:8080/lobby/test_game?player=TestPlayer');

ws.onopen = () => {
  console.log('✅ WebSocket 연결 성공!');
};

ws.onmessage = (event) => {
  const message = JSON.parse(event.data);
  console.log('📨 수신 메시지:', message);
};

ws.onerror = (error) => {
  console.error('❌ WebSocket 에러:', error);
};

ws.onclose = (event) => {
  console.log('🔌 연결 종료:', event.code, event.reason);
};
```

### 2. curl로 테스트 (PowerShell)

```powershell
# WebSocket 연결 테스트 (간단한 HTTP 요청으로 확인)
Invoke-WebRequest -Uri http://192.168.0.10:8080/health -UseBasicParsing
```

---

## 📋 체크리스트

연결 문제가 발생하면 다음을 확인하세요:

- [ ] 서버가 실행 중인가? (`http://localhost:8080/health` 확인)
- [ ] 올바른 IP 주소를 사용하는가? (`10.0.2.2` ❌ → `192.168.0.10` 또는 `localhost` ✅)
- [ ] 올바른 포트를 사용하는가? (`8080`)
- [ ] 올바른 엔드포인트 경로를 사용하는가? (`/lobby/{game_id}`)
- [ ] 쿼리 파라미터가 올바른가? (`?player={playerName}`)
- [ ] 플레이어 이름이 URL 인코딩되었는가? (`encodeURIComponent` 사용)
- [ ] 방화벽이 포트 8080을 차단하지 않는가?
- [ ] 프론트엔드와 백엔드가 같은 네트워크에 있는가?

---

## 🔧 추가 문제 해결

### 방화벽 확인

Windows 방화벽에서 포트 8080이 허용되어 있는지 확인:

```powershell
# 방화벽 규칙 확인
Get-NetFirewallRule | Where-Object {$_.DisplayName -like "*8080*"}

# 방화벽 규칙 추가 (필요시)
New-NetFirewallRule -DisplayName "Ledger Weight Backend" -Direction Inbound -LocalPort 8080 -Protocol TCP -Action Allow
```

### 서버 재시작

서버를 재시작해야 할 경우:

```powershell
# 서버 중지: Ctrl+C
# 서버 재시작
.\start_server.ps1
```

---

## 📞 문의

추가 문제가 발생하면 다음 정보를 포함하여 문의해주세요:

1. 사용 중인 IP 주소
2. 에러 메시지 전체 내용
3. 브라우저/앱 환경 (Chrome, Android 에뮬레이터 등)
4. 네트워크 환경 (같은 Wi-Fi, 다른 네트워크 등)

---

**작성자**: 백엔드 개발자  
**최종 업데이트**: 2025-12-12

