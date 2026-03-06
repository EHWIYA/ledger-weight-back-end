# 시스템 아키텍처 설계

## 개요
WebSocket 기반 실시간 카드 게임 '장부의 무게'의 시스템 아키텍처 설계 문서입니다.

## 시스템 구성

```
┌─────────────┐
│   Client    │ (React Native)
│  (Mobile)   │
└──────┬──────┘
       │ WebSocket
       │ (실시간 통신)
       ▼
┌─────────────────┐
│   FastAPI       │
│   Server        │
│                 │
│  ┌───────────┐  │
│  │ WebSocket │  │
│  │ Handler   │  │
│  └─────┬─────┘  │
│        │        │
│  ┌─────▼─────┐  │
│  │ Game      │  │
│  │ Manager   │  │
│  └─────┬─────┘  │
│        │        │
│  ┌─────▼─────┐  │
│  │ Models    │  │
│  │ (In-Memory)│ │
│  └───────────┘  │
└─────────────────┘
```

## 아키텍처 패턴

### 선택한 패턴: 레이어드 아키텍처 (Layered Architecture)

**레이어 구성**:
1. **Presentation Layer**: WebSocket 핸들러, REST API
2. **Application Layer**: 게임 로직 (Game Manager, Action Handler)
3. **Domain Layer**: 도메인 모델 (Player, Card, Game)
4. **Infrastructure Layer**: 설정, 유틸리티

## 의사결정 기록

### 1. 데이터 저장 방식
**선택한 방식**: 인메모리 (In-Memory) 저장

**이유**:
- 실시간 게임 특성상 빠른 응답 필요
- 게임 세션은 일시적 (게임 종료 시 데이터 삭제)
- 단순한 구조로 빠른 개발 가능

**대안 고려**:
- 데이터베이스 저장: 게임 히스토리 저장이 필요할 때만 고려
- Redis: 향후 확장 시 고려 가능

**코드 예시**:
```python
# app/game/game_manager.py
class GameManager:
    def __init__(self):
        self.games: Dict[str, Game] = {}  # 게임 ID -> Game 인스턴스
        self.players: Dict[str, Player] = {}  # 플레이어 ID -> Player 인스턴스
```

### 2. WebSocket 통신 방식
**선택한 방식**: FastAPI WebSocket + Connection Manager

**이유**:
- FastAPI 네이티브 지원
- 비동기 처리 지원
- 연결 관리 용이

**코드 예시**:
```python
# app/websocket/connection_manager.py
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
    
    async def connect(self, websocket: WebSocket, player_id: str):
        await websocket.accept()
        self.active_connections[player_id] = websocket
    
    async def broadcast(self, message: dict):
        for connection in self.active_connections.values():
            await connection.send_json(message)
```

### 3. 게임 상태 관리
**선택한 방식**: 상태 기반 (State-based) 업데이트

**이유**:
- 클라이언트와 서버 상태 동기화 용이
- 전체 상태를 주기적으로 전송하여 일관성 보장
- 디버깅 용이

**메시지 구조**:
```python
# GAME_STATE_UPDATE 메시지 예시
{
    "type": "GAME_STATE_UPDATE",
    "current_player_id": "player_1",
    "turn_state": "PLAY_CARD",
    "players": [
        {
            "id": "player_1",
            "hp": 5,
            "range": 1,
            "hand_count": 5,
            "treasure": "황금 연갑"
        }
    ],
    "event": "플레이어 1이 정산 카드를 사용했습니다"
}
```

## 트러블슈팅

### 이슈: WebSocket 연결 관리
**문제**: 다중 플레이어 게임에서 연결 관리 복잡성

**해결 방안**:
- ConnectionManager 클래스로 중앙 집중식 관리
- 플레이어 ID와 WebSocket 연결 매핑
- 연결 해제 시 자동 정리

### 이슈: 게임 상태 동기화
**문제**: 클라이언트와 서버 상태 불일치 가능성

**해결 방안**:
- 서버가 단일 진실의 원천 (Single Source of Truth)
- 모든 액션은 서버에서 검증 후 처리
- 상태 변경 시 모든 클라이언트에 브로드캐스트

## 성능 고려사항

### 1. WebSocket 연결 관리
**최적화 포인트**:
- 연결 풀 크기 제한 (`WS_MAX_CONNECTIONS`)
- 하트비트 메커니즘으로 데드 연결 감지
- 연결 해제 시 즉시 정리

### 2. 게임 상태 업데이트
**최적화 포인트**:
- 변경된 부분만 전송 (Delta Update) 고려
- 현재는 전체 상태 전송 (단순성 우선)
- 향후 성능 문제 시 최적화

### 3. 메모리 관리
**고려사항**:
- 게임 종료 시 인스턴스 즉시 삭제
- 장기 실행 시 메모리 누수 방지
- 게임 수 제한 (필요시)

## 확장성 고려사항

### 단기 (현재)
- 단일 서버 인스턴스
- 인메모리 게임 상태
- 직접 WebSocket 통신

### 중기 (향후)
- 다중 게임 룸 지원
- 게임 히스토리 저장 (선택적)
- 플레이어 매칭 시스템

### 장기 (확장 시)
- Redis를 통한 게임 상태 공유
- 마이크로서비스 아키텍처 고려
- 로드 밸런싱 및 수평 확장

## 보안 고려사항

1. **입력 검증**: 모든 클라이언트 입력은 Pydantic으로 검증
2. **액션 권한**: 현재 턴 플레이어만 액션 가능
3. **WebSocket 인증**: 연결 시 인증 토큰 검증 (향후 구현)
4. **Rate Limiting**: 액션 빈도 제한 (향후 구현)

