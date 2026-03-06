# FastAPI 베스트 프랙티스 적용

## 개요
프로젝트에서 적용한 FastAPI 베스트 프랙티스 및 설계 원칙을 문서화합니다.

## 적용된 베스트 프랙티스

### 1. 타입 힌팅
**원칙**: 모든 함수와 변수에 타입 힌팅 적용

**코드 예시**:
```python
from typing import Dict, List, Optional

def get_player(player_id: str) -> Optional[Player]:
    """플레이어 조회"""
    return self.players.get(player_id)
```

**이유**:
- IDE 자동완성 향상
- 런타임 전 오류 발견
- 코드 가독성 향상

### 2. Pydantic 모델 활용
**원칙**: 모든 데이터 구조는 Pydantic 모델로 정의

**코드 예시**:
```python
from pydantic import BaseModel

class PlayerAction(BaseModel):
    action_type: ActionType
    player_id: str
    data: Dict[str, any]
```

**이유**:
- 자동 검증
- API 문서 자동 생성
- 타입 안정성

### 3. 비동기 처리
**원칙**: I/O 작업은 모두 비동기로 처리

**코드 예시**:
```python
async def broadcast_game_state(self, game_id: str):
    """게임 상태 브로드캐스트"""
    game_state = await self.get_game_state(game_id)
    await self.connection_manager.broadcast(game_state)
```

**이유**:
- 동시성 향상
- WebSocket 통신에 최적화
- 확장성 향상

### 4. 의존성 주입
**원칙**: 의존성은 생성자 주입 또는 FastAPI Depends 활용

**코드 예시**:
```python
from fastapi import Depends

def get_game_manager() -> GameManager:
    return game_manager

@app.websocket("/ws/{game_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    game_manager: GameManager = Depends(get_game_manager)
):
    ...
```

**이유**:
- 테스트 용이성
- 느슨한 결합
- 재사용성 향상

## 의사결정 기록

### 1. 설정 관리: Pydantic Settings
**선택한 방식**: `pydantic-settings` 사용

**이유**:
- 환경 변수 자동 로딩
- 타입 검증
- `.env` 파일 지원
- FastAPI와 자연스러운 통합

**대안 고려**:
- `python-decouple`: 기능 부족
- 직접 `os.getenv()`: 타입 안정성 부족

### 2. 로깅: Loguru
**선택한 방식**: `loguru` 사용

**이유**:
- 간단한 설정
- 구조화된 로깅
- 비동기 지원
- 자동 로테이션

**코드 예시**:
```python
from loguru import logger

logger.info("게임 시작", game_id=game_id, players=len(players))
```

### 3. 코드 포맷팅: Black + Ruff
**선택한 방식**: Black (포맷팅) + Ruff (린팅)

**이유**:
- 빠른 실행 속도
- 일관된 코드 스타일
- 자동 수정 가능

## 트러블슈팅

### 이슈: CORS 설정
**문제**: 프론트엔드에서 WebSocket 연결 실패

**해결**:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**참고**: 프로덕션에서는 특정 origin만 허용해야 함

### 이슈: WebSocket 연결 유지
**문제**: 클라이언트 연결 끊김 감지 어려움

**해결 방안**:
- 하트비트 메커니즘 구현 예정
- 연결 상태 주기적 체크

## 성능 고려사항

### 1. 비동기 처리
- 모든 I/O 작업은 `async/await` 사용
- 동기 블로킹 작업 최소화

### 2. 연결 관리
- WebSocket 연결 풀 크기 제한
- 데드 연결 자동 정리

### 3. 메모리 관리
- 게임 인스턴스 생명주기 관리
- 불필요한 데이터 즉시 삭제

## 향후 개선 사항

1. **인증/인가**: JWT 토큰 기반 인증
2. **Rate Limiting**: 액션 빈도 제한
3. **모니터링**: Prometheus + Grafana
4. **로깅**: 구조화된 로깅 및 중앙 집중식 관리

