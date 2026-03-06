# FastAPI 개념 (초보자용)

FastAPI의 핵심 개념을 이 프로젝트 기준으로 설명합니다.

---

## 1. FastAPI() 앱 인스턴스

### 이게 뭔가요?
모든 라우트, 미들웨어, 의존성의 **진입점**입니다. `app = FastAPI()`로 생성하고, uvicorn이 `app.main:app`으로 로드합니다.

### 이 프로젝트에서 어떻게 쓰나요?
- `app/main.py`: `app = FastAPI(title=..., docs_url="/docs", redoc_url="/redoc")`

---

## 2. 라우트 데코레이터

### 이게 뭔가요?
`@app.get("/")`, `@app.websocket("/lobby/...")`처럼 **URL 경로와 함수를 연결**하는 문법입니다.

### 이 프로젝트에서 어떻게 쓰나요?
- `@app.get("/")` — 루트
- `@app.get("/health")` — 헬스 체크
- `@app.websocket("/lobby/{game_id}")` — 로비 WebSocket
- `@app.websocket("/ws/{player_id}")` — WebSocket (호환용)

### 예시
```python
@app.get("/health")
async def health_check():
    return {"status": "healthy"}
```

---

## 3. 미들웨어

### 이게 뭔가요?
요청이 라우트에 도달하기 **전/후**에 실행되는 처리기입니다. CORS, 로깅, 인증 등에 사용합니다.

### 이 프로젝트에서 어떻게 쓰나요?
- `CORSMiddleware`: 브라우저 cross-origin 요청 허용

### 예시
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
)
```

---

## 4. WebSocket

### 이게 뭔가요?
**양방향 실시간 통신**을 위한 프로토콜입니다. HTTP처럼 요청-응답이 아니라, 연결을 유지한 채로 메시지를 주고받습니다.

### 이 프로젝트에서 어떻게 쓰나요?
- `WebSocket` 타입으로 연결 수락
- `accept()`, `receive_text()`, `send_json()` 사용
- `connection_manager`로 연결 관리

### 예시
```python
@app.websocket("/lobby/{game_id}")
async def lobby_websocket_endpoint(websocket: WebSocket, game_id: str, player: str = Query(...)):
    await websocket.accept()
    await websocket.send_json({"type": "CONNECTION_ESTABLISHED", "player_id": player_id})
```

---

## 5. Query / Path

### 이게 뭔가요?
- **Query**: URL 쿼리 파라미터 (`?player=홍길동`)
- **Path**: URL 경로 파라미터 (`/lobby/game_123`)

### 이 프로젝트에서 어떻게 쓰나요?
- `game_id: str` — Path
- `player: str = Query(...)` — Query (필수)
- `token: Optional[str] = Query(default=None)` — Query (선택)

---

## 6. 자동 문서화

### 이게 뭔가요?
FastAPI가 라우트를 분석해 **Swagger UI**와 **ReDoc**을 자동 생성합니다.

### 이 프로젝트에서 어떻게 쓰나요?
- `/docs` — Swagger UI
- `/redoc` — ReDoc
