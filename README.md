# Ledger Weight · 실시간 카드 게임 서버

‘장부의 무게’는 BANG! 카드 게임을 바탕으로 만든 포트폴리오 프로젝트입니다.
FastAPI와 WebSocket을 사용해 실시간 통신과 게임 로직을 처리하는 백엔드 서버입니다.

## 담당한 구현과 문제 해결

FastAPI 백엔드에서 게임 상태의 WebSocket 전달, 메시지 처리와 응답 스키마를 보완했습니다.
아래 변경은 EHWIYA 계정의 커밋으로 확인할 수 있습니다.

### 1. 연결 확인 메시지와 게임 메시지의 처리 구분

이전 수신 루프는 `PING`도 일반 메시지 핸들러로 넘겼습니다.
연결 확인 요청을 별도로 처리하도록 수신 루프에서 `PONG`을 반환한 뒤 게임 메시지 처리를 건너뛰게 구성했습니다.

잘못된 JSON에는 `ERROR / INVALID_JSON`을 반환하고, 메시지 핸들러에서는
지원하지 않는 타입과 처리 중 오류를 코드로 구분합니다.
연결 확인, 입력 형식 오류, 게임 동작 결과를 각각 해석할 수 있도록 응답 경계를 나눴습니다.

- **반영 내용:** PING/PONG 처리와 오류 코드 추가
- **현재 구조:** [공통 수신 루프](app/main.py) → [메시지 타입별 처리](app/websocket/message_handler.py)
- **근거:** [하트비트·오류 응답 정리 커밋](https://github.com/EHWIYA/ledger-weight-back-end/commit/d560c7c9e2583a52618b28e926d0521632f19e4c)

### 2. 게임 모델과 프런트엔드 응답 필드의 차이

게임 내부의 체력 값은 `hp`이지만 프런트엔드 응답에는 `wealth` 필드도 필요했습니다.
모델 값을 그대로 전달하는 대신 `Player.to_dict()`에서 `wealth: int(self.hp)`를 반환하도록 추가했습니다.

- **기술적 판단:** 내부 게임 모델을 유지하면서 직렬화 경계에서 화면의 필드 계약을 맞춤
- **확인 가능한 변경:** `wealth` 필드와 정수 변환 추가
- **근거:** [응답 필드 보장 커밋](https://github.com/EHWIYA/ledger-weight-back-end/commit/787cdf43dae3974d12944d4aa052aed23629408b) · [Player 직렬화](app/models/player.py)

## 코드에서 확인할 수 있는 설계 선택

### 같은 게임에서도 플레이어마다 다른 상태 전달

플레이어별로 자신에게 보이는 패와 상대에게 보이는 정보가 다릅니다.
게임 상태를 한 번 만들어 모두에게 전송하는 대신, 수신할 플레이어 ID로 상태를 직렬화해 개별 전송합니다.

```text
broadcast_game_state(game_id)
  → 플레이어별 send_game_state_to_player(player_id, game_id)
  → Game.to_dict(player_id)
  → 본인의 패는 포함, 상대의 패는 빈 배열과 카드 수로 표현
```

공개 상태와 개인에게만 보이는 상태를 서버의 응답 생성 단계에서 구분했습니다.

[플레이어별 상태 전송](app/websocket/message_handler.py) · [Game 직렬화](app/models/game.py) · [Player 직렬화](app/models/player.py)

## 검증 자료와 범위

- [헬스 체크 테스트](tests/test_health.py): 서버 정보와 `/health` 응답 확인
- [게임 시뮬레이션 스크립트](scripts/simulate_games.py): 게임 로직을 반복 실행하는 확인 경로

헬스 체크는 전체 게임 규칙이나 플레이어별 비공개 정보 처리를 보장하지 않습니다.
시뮬레이션도 실제 WebSocket 다중 접속·재연결·부하 검증과 구분해야 합니다.

<details>
<summary>기술 스택·개발 문서·로컬 실행 안내</summary>

## 핵심 구성

- WebSocket 기반 플레이어 연결
- 게임 로직과 WebSocket 메시지 처리
- HTTP 상태 확인 API와 Swagger 문서

| 영역 | 기술 |
| --- | --- |
| 언어·프레임워크 | Python, FastAPI |
| 실시간 통신 | WebSocket |
| 서버 실행 | Uvicorn |

## 구현 살펴보기

- [프로젝트 문서](docs/README.md)
- [문서 인덱스](docs/INDEX.md)
- [서버 코드](app/)
- [변경 이력](https://github.com/EHWIYA/ledger-weight-back-end/commits)

게임 로직, 메시지 처리와 서버 구성은 코드와 문서에서 확인할 수 있습니다.

## 로컬 실행

```bash
pip install -r requirements.txt
cp env.example .env
# .env 파일을 열어서 필요한 설정 수정
uvicorn app.main:app --reload
```

NAS 배포 구성의 기본 포트는 `8088`이며, 실행 명령은 다음과 같습니다.

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8088
```

## Endpoint

| 방식 | 경로 | 용도 |
| --- | --- | --- |
| GET | `/` | 서버 정보 |
| GET | `/health` | 헬스 체크 |
| GET | `/docs` | Swagger UI |
| GET | `/redoc` | ReDoc |
| WebSocket | `/ws/{player_id}` | 플레이어 연결 |

## 개발 환경

기존 README의 기준은 Python 3.8+, FastAPI 0.104.1, Uvicorn 0.24.0입니다.
실제 설치 버전은 저장소의 `requirements.txt`를 기준으로 확인하세요.


</details>

