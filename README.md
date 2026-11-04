# Ledger Weight · 실시간 카드 게임 서버

‘장부의 무게’는 BANG! 카드 게임을 바탕으로 만든 포트폴리오 프로젝트입니다.
FastAPI와 WebSocket을 사용해 실시간 통신과 게임 로직을 처리하는 백엔드 서버입니다.

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

