# 프로젝트 구조 설계

## 개요
FastAPI 기반 WebSocket 실시간 카드 게임 서버의 프로젝트 구조 설계 문서입니다.

## 최종 구조

```
ledger-weight-back-end/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI 앱 진입점
│   ├── config.py               # 설정 관리
│   ├── models/                 # 데이터 모델
│   │   ├── __init__.py
│   │   ├── player.py           # Player 모델
│   │   ├── card.py             # Card 모델
│   │   ├── game.py             # Game 모델
│   │   └── role.py             # Role 모델
│   ├── game/                   # 게임 로직
│   │   ├── __init__.py
│   │   ├── game_manager.py     # 게임 상태 관리
│   │   ├── card_manager.py     # 카드 덱 관리
│   │   ├── turn_manager.py     # 턴 관리
│   │   └── action_handler.py   # 액션 처리
│   ├── websocket/              # WebSocket 핸들러
│   │   ├── __init__.py
│   │   ├── connection_manager.py
│   │   └── message_handler.py
│   ├── api/                    # REST API (필요시)
│   │   └── routes.py
│   └── utils/                  # 유틸리티
│       ├── constants.py        # 상수 정의
│       └── validators.py
├── tests/                      # 테스트
├── docs/                       # 문서
└── logs/                       # 작업일지
```

## 의사결정 기록

### 1. 모듈 분리 전략
**선택한 방식**: 기능별 모듈 분리 (models, game, websocket, api, utils)

**이유**:
- 단일 책임 원칙 (SRP) 준수
- 코드 재사용성 향상
- 테스트 용이성
- 팀 협업 시 충돌 최소화

**대안 고려**:
- 도메인 주도 설계 (DDD) 방식도 고려했으나, 프로젝트 규모상 과도함
- 단일 파일 구조는 유지보수 어려움

### 2. 설정 관리 방식
**선택한 방식**: Pydantic Settings (`pydantic-settings`)

**이유**:
- 타입 안정성 보장
- 환경 변수 자동 로딩
- 검증 기능 내장
- FastAPI와의 자연스러운 통합

**코드 예시**:
```python
# app/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "장부의 무게 API"
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
```

### 3. 상수 관리 방식
**선택한 방식**: Enum 클래스 + 별도 constants.py 파일

**이유**:
- 타입 안정성 (IDE 자동완성)
- 오타 방지
- 가독성 향상
- 리팩토링 용이

**코드 예시**:
```python
# app/utils/constants.py
from enum import Enum

class Role(str, Enum):
    SHERIFF = "상단주"
    DEPUTY = "원로원"
    OUTLAW = "적도 세력"
    RENEGADE = "야망가"
```

## 트러블슈팅

### 이슈 1: Git 커밋 메시지 한글 깨짐
**문제**: PowerShell에서 직접 한글 커밋 메시지를 전달할 때 인코딩 문제 발생

**해결 과정**:
1. `chcp 65001` (UTF-8 코드 페이지 설정) 시도 → 실패
2. 환경 변수 설정 시도 → 실패
3. **최종 해결**: 임시 파일을 통한 커밋 메시지 전달

**해결 코드**:
```python
# 커밋 메시지를 파일로 저장
with open("commit_msg.txt", "w", encoding="utf-8") as f:
    f.write("251211 > back-end > fast-api > 작업내용")

# 파일을 통한 커밋
git commit -F commit_msg.txt
```

**향후 대응**: 한글이 포함된 커밋 메시지는 항상 파일을 통해 전달

### 이슈 2: PowerShell 출력 한글 깨짐
**문제**: 디렉토리 목록 확인 시 한글이 깨져서 표시됨

**해결**:
```powershell
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8
chcp 65001 | Out-Null
```

**향후 대응**: 모든 PowerShell 명령어 실행 전 인코딩 설정 적용

## 성능 고려사항

### 1. 모듈 임포트 최적화
**고려사항**: 
- 순환 참조 방지
- 지연 임포트 (lazy import) 고려
- `__init__.py`에서 필요한 것만 export

**최적화 포인트**:
```python
# app/models/__init__.py
# 필요한 것만 export하여 불필요한 임포트 방지
from .player import Player
from .card import Card
# ... 나머지는 필요시 직접 임포트
```

### 2. 설정 로딩 최적화
**고려사항**:
- 설정은 앱 시작 시 한 번만 로드
- 전역 인스턴스로 관리하여 재사용

**현재 구현**:
```python
# app/config.py
settings = Settings()  # 전역 인스턴스
```

### 3. 향후 확장성 고려
- 다중 게임 룸 지원을 위한 구조 설계
- 게임 인스턴스 관리 방식 (메모리 vs DB)
- WebSocket 연결 풀 관리 전략

## 다음 단계
- [ ] 기본 모델 클래스 구현 및 문서화
- [ ] 게임 로직 구현 및 문서화
- [ ] WebSocket 통신 구현 및 문서화

