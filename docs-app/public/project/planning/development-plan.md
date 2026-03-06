# 개발 계획서

## Phase 1: 프로젝트 초기 설정 (1주차)

### 1.1 프로젝트 구조 설계
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

### 1.2 의존성 관리
- `requirements.txt` 또는 `pyproject.toml` 생성
- FastAPI, WebSocket, Pydantic 등 필수 패키지 설치

### 1.3 환경 설정
- `.env` 파일 템플릿 생성
- 설정 관리 시스템 구축

## Phase 2: 핵심 모델 및 상수 정의 (1-2주차)

### 2.1 상수 정의 (`utils/constants.py`)
- 카드 타입 상수
- 역할 상수
- 액션 타입 상수
- 게임 상태 상수

### 2.2 카드 모델 (`models/card.py`)
- 카드 기본 속성 (이름, 타입, 무늬, 숫자, 영향력)
- 카드 기능 정의
- 카드 덱 생성 로직

### 2.3 플레이어 모델 (`models/player.py`)
- 플레이어 기본 속성 (ID, 재력, 영향력)
- 핸드 카드 관리
- 장착 보물 관리
- 역할 정보

### 2.4 게임 모델 (`models/game.py`)
- 게임 상태 관리
- 플레이어 목록 관리
- 덱/버림 더미 관리
- 턴 정보

## Phase 3: 게임 로직 구현 (2-4주차)

### 3.1 카드 관리자 (`game/card_manager.py`)
- 덱 생성 및 셔플
- 카드 드로우
- 카드 버리기
- 덱 재생성 로직

### 3.2 게임 매니저 (`game/game_manager.py`)
- 게임 초기화
- 플레이어 추가/제거
- 게임 상태 업데이트
- 승리 조건 체크

### 3.3 턴 관리자 (`game/turn_manager.py`)
- 턴 순서 관리
- 턴 단계 관리 (DRAW, PLAY_CARD, END_TURN)
- 턴 종료 처리

### 3.4 액션 핸들러 (`game/action_handler.py`)
- 카드 사용 처리
- 공격/방어 처리
- 특수 카드 처리
- 보물 능력 처리

## Phase 4: WebSocket 통신 구현 (3-4주차)

### 4.1 연결 관리자 (`websocket/connection_manager.py`)
- WebSocket 연결 관리
- 플레이어-연결 매핑
- 브로드캐스트 기능

### 4.2 메시지 핸들러 (`websocket/message_handler.py`)
- `PLAYER_ACTION` 메시지 처리
- `GAME_STATE_UPDATE` 메시지 생성 및 전송
- 에러 처리

### 4.3 WebSocket 엔드포인트
- 게임 입장
- 게임 상태 구독
- 액션 전송

## Phase 5: 게임 규칙 세부 구현 (4-6주차)

### 5.1 카드 기능 구현
- 기본 공격/방어 카드
- 무기 카드
- 장착 카드
- 특수 카드

### 5.2 보물 능력 구현
- 16종 보물 각각의 능력 구현
- 보물 간 상호작용 처리

### 5.3 게임 규칙 검증
- 액션 유효성 검증
- 승리 조건 체크
- 게임 종료 처리

## Phase 6: 테스트 및 문서화 (5-6주차)

### 6.1 단위 테스트
- 각 모델 테스트
- 게임 로직 테스트
- WebSocket 통신 테스트

### 6.2 통합 테스트
- 전체 게임 플로우 테스트
- 다중 플레이어 시나리오 테스트

### 6.3 문서화
- API 문서 (FastAPI 자동 생성)
- 게임 로직 문서
- WebSocket 프로토콜 문서
- 배포 가이드

## 우선순위 작업 목록

### 즉시 시작 (이번 주)
1. ✅ 프로젝트 폴더 구조 생성
2. ✅ 의존성 파일 생성 (`requirements.txt` 또는 `pyproject.toml`)
3. ✅ 기본 설정 파일 생성
4. ✅ 상수 정의 (`utils/constants.py`)
5. ✅ 기본 모델 클래스 정의 (Card, Player, Game)

### 다음 주
6. 카드 덱 생성 로직 구현
7. 게임 매니저 기본 구조 구현
8. WebSocket 기본 연결 구현
9. 간단한 게임 상태 전송 테스트

### 단기 목표 (2-3주)
10. 기본 카드 사용 로직 구현
11. 턴 관리 시스템 구현
12. 공격/방어 메커니즘 구현

### 중기 목표 (4-6주)
13. 모든 카드 타입 구현
14. 보물 능력 구현
15. 게임 종료 및 승리 조건 처리

## 기술적 고려사항

### 성능
- WebSocket 연결 풀 관리
- 게임 상태 업데이트 최적화
- 메모리 관리 (게임 인스턴스)

### 확장성
- 다중 게임 룸 지원 가능한 구조
- 플레이어 매칭 시스템 고려
- 게임 히스토리 저장 (선택사항)

### 보안
- 입력 검증
- 액션 권한 검증
- WebSocket 연결 인증

