# 데이터베이스 선택 가이드

**작성일**: 2025-12-11  
**프로젝트**: 장부의 무게 (WebSocket 기반 실시간 카드 게임)

---

## 📋 현재 상태 분석

### 현재 데이터 저장 방식
- **게임 상태**: 메모리 (Dict) - `GameManager.games: Dict[str, Game]`
- **플레이어 정보**: 메모리 (게임 세션 동안만)
- **카드 덱**: 메모리 (게임 세션 동안만)
- **이벤트 로그**: 메모리 (최근 50개만)

### 데이터 특성
- ✅ **실시간성**: 게임 진행 중 매우 빠른 읽기/쓰기 필요
- ✅ **임시성**: 게임 세션은 일시적 (게임 종료 후 대부분 불필요)
- ✅ **단순성**: 복잡한 관계형 쿼리 불필요
- ✅ **세션 관리**: WebSocket 연결 및 게임 상태 관리
- ⚠️ **영구 저장**: 게임 통계, 플레이어 기록 (선택사항)

---

## 🎯 추천 옵션

### 옵션 1: Redis (⭐ 가장 추천)

#### 장점
- ✅ **매우 빠른 성능**: 인메모리 저장, 초당 수만 건 처리 가능
- ✅ **실시간 게임에 최적**: 낮은 지연시간 (1ms 이하)
- ✅ **세션 관리**: TTL(Time To Live) 지원으로 자동 만료
- ✅ **데이터 구조 다양**: String, Hash, List, Set, Sorted Set
- ✅ **게임 상태 저장에 적합**: JSON 직렬화 가능
- ✅ **Pub/Sub 지원**: 실시간 알림에 활용 가능
- ✅ **설치 및 운영 간단**: 경량, 빠른 시작

#### 단점
- ⚠️ **메모리 제한**: RAM 용량에 따라 제한
- ⚠️ **영구 저장 불가**: 서버 재시작 시 데이터 손실 (AOF/RDB로 보완 가능)
- ⚠️ **복잡한 쿼리 불가**: 관계형 쿼리 불가

#### 사용 시나리오
```python
# 게임 상태 저장
redis.setex(f"game:{game_id}", 3600, json.dumps(game_state))  # 1시간 TTL

# 플레이어 세션 관리
redis.hset(f"player:{player_id}", mapping={
    "name": player_name,
    "game_id": game_id,
    "connected_at": timestamp
})
redis.expire(f"player:{player_id}", 7200)  # 2시간 TTL

# 게임 목록 조회
redis.keys("game:*")
```

#### 설치 및 설정
```bash
# Ubuntu
sudo apt-get install redis-server
sudo systemctl start redis-server
sudo systemctl enable redis-server

# Python 패키지
pip install redis
```

---

### 옵션 2: PostgreSQL (영구 저장 필요 시)

#### 장점
- ✅ **안정성**: 검증된 관계형 DB
- ✅ **영구 저장**: 게임 통계, 플레이어 기록 저장
- ✅ **복잡한 쿼리**: JOIN, 집계 함수 등
- ✅ **트랜잭션**: ACID 보장
- ✅ **확장성**: 대용량 데이터 처리

#### 단점
- ⚠️ **성능**: Redis보다 느림 (디스크 I/O)
- ⚠️ **설정 복잡**: 초기 설정 및 튜닝 필요
- ⚠️ **오버킬**: 실시간 게임에는 과도할 수 있음

#### 사용 시나리오
- 게임 통계 저장
- 플레이어 전적 기록
- 게임 히스토리 저장
- 분석 및 리포트

#### 설치 및 설정
```bash
# Ubuntu
sudo apt-get install postgresql postgresql-contrib
sudo systemctl start postgresql

# Python 패키지
pip install psycopg2-binary sqlalchemy alembic
```

---

### 옵션 3: 하이브리드 (Redis + PostgreSQL) ⭐⭐

#### 구성
- **Redis**: 실시간 게임 상태, 세션 관리
- **PostgreSQL**: 게임 통계, 플레이어 기록, 영구 저장

#### 장점
- ✅ **최고 성능**: Redis로 실시간 처리
- ✅ **데이터 보존**: PostgreSQL로 영구 저장
- ✅ **유연성**: 용도에 따라 적절한 DB 선택

#### 단점
- ⚠️ **복잡도 증가**: 두 개의 DB 관리
- ⚠️ **동기화 필요**: Redis → PostgreSQL 데이터 동기화

#### 사용 시나리오
```python
# 게임 진행 중: Redis
redis.setex(f"game:{game_id}", 3600, game_state_json)

# 게임 종료 시: PostgreSQL에 통계 저장
db.execute("""
    INSERT INTO game_history (game_id, winner, players, duration)
    VALUES (:game_id, :winner, :players, :duration)
""")
```

---

### 옵션 4: 현재 상태 유지 (메모리 기반)

#### 장점
- ✅ **가장 빠름**: 메모리 직접 접근
- ✅ **설정 불필요**: DB 설치/관리 없음
- ✅ **단순함**: 코드 복잡도 최소

#### 단점
- ❌ **서버 재시작 시 데이터 손실**: 모든 게임 상태 초기화
- ❌ **확장성 제한**: 단일 서버만 가능
- ❌ **영구 저장 불가**: 통계/기록 저장 불가

#### 개선 방안
- 게임 종료 시 파일로 저장 (JSON)
- 주기적으로 스냅샷 저장
- Redis로 마이그레이션 (권장)

---

## 🎯 최종 추천

### 단계별 추천

#### 1단계: 개발/테스트 단계 (현재)
**추천**: **현재 상태 유지 (메모리 기반)**
- 빠른 개발 및 테스트
- DB 설정 부담 없음
- 프로토타입 단계에 적합

#### 2단계: 프로덕션 준비
**추천**: **Redis**
- 실시간 게임에 최적
- 설치 및 운영 간단
- 성능 우수
- 세션 관리 용이

#### 3단계: 통계/기록 필요 시
**추천**: **Redis + PostgreSQL (하이브리드)**
- Redis: 실시간 게임 상태
- PostgreSQL: 게임 통계, 플레이어 기록

---

## 📊 비교표

| 항목 | Redis | PostgreSQL | 하이브리드 | 메모리(현재) |
|------|-------|------------|-----------|-------------|
| **성능** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **설정 난이도** | ⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ |
| **영구 저장** | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ❌ |
| **실시간성** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **확장성** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ |
| **복잡도** | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ |

---

## 💡 구현 가이드

### Redis 도입 시 변경사항

#### 1. 의존성 추가
```bash
pip install redis
```

#### 2. Redis 클라이언트 설정
```python
# app/database/redis_client.py
import redis
from app.config import settings

redis_client = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=0,
    decode_responses=True
)
```

#### 3. GameManager 수정
```python
# app/game/game_manager.py
import json
from app.database.redis_client import redis_client

class GameManager:
    def __init__(self):
        # 메모리 캐시 (빠른 접근)
        self.games_cache: Dict[str, Game] = {}
        self.card_managers: Dict[str, CardManager] = {}
    
    def get_game(self, game_id: str) -> Optional[Game]:
        # 캐시에서 먼저 확인
        if game_id in self.games_cache:
            return self.games_cache[game_id]
        
        # Redis에서 조회
        game_data = redis_client.get(f"game:{game_id}")
        if game_data:
            game_dict = json.loads(game_data)
            game = Game(**game_dict)
            self.games_cache[game_id] = game
            return game
        
        return None
    
    def save_game(self, game_id: str, game: Game) -> None:
        # 캐시에 저장
        self.games_cache[game_id] = game
        
        # Redis에 저장 (1시간 TTL)
        game_json = json.dumps(game.dict())
        redis_client.setex(f"game:{game_id}", 3600, game_json)
```

#### 4. 설정 파일 수정
```python
# app/config.py
class Settings(BaseSettings):
    # Redis 설정
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
```

---

## 🚀 마이그레이션 계획

### Phase 1: Redis 도입 (1주)
1. Redis 설치 및 설정
2. Redis 클라이언트 구현
3. GameManager에 Redis 통합
4. 테스트 및 검증

### Phase 2: 영구 저장 (필요 시)
1. PostgreSQL 설치 및 설정
2. 게임 통계 스키마 설계
3. 게임 종료 시 통계 저장 로직
4. 통계 조회 API 구현

---

## 📌 결론

### 즉시 추천: **Redis**
- 실시간 게임 서버에 최적
- 설치 및 운영 간단
- 성능 우수
- 현재 메모리 기반에서 쉽게 마이그레이션 가능

### 장기 추천: **Redis + PostgreSQL (하이브리드)**
- Redis: 실시간 게임 상태
- PostgreSQL: 게임 통계 및 기록
- 최고의 성능과 데이터 보존

---

**작성자**: 백엔드 개발자  
**최종 업데이트**: 2025-12-11

