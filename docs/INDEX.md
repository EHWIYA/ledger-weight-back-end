# 문서 인덱스

빠른 문서 탐색을 위한 인덱스입니다. 에이전트는 이 문서를 참고해 적절한 문서를 선택하세요.

---

## 시각화

- **문서 대시보드**: 서버 실행 후 `http://localhost:8088/docs-view/` 접속
- **시각화 가이드**: [docs/visual-guide/index.html](visual-guide/index.html) — 프로젝트 구조, HTTP/WebSocket 흐름, Python·FastAPI·라이브러리 개념 (Mermaid)

---

## 개념 (학습용, 초보자급)

| 문서 | 경로 | 용도 |
|------|------|------|
| Python | [concepts/python.md](concepts/python.md) | async, 타입 힌트, Enum, 클래스, 패키지 |
| FastAPI | [concepts/fastapi.md](concepts/fastapi.md) | 앱, 라우트, 미들웨어, WebSocket, Query/Path |
| GitHub/Git | [concepts/github-git.md](concepts/github-git.md) | 커밋, 브랜치, GitHub Actions |
| Docker | [concepts/docker.md](concepts/docker.md) | Dockerfile, docker-compose, 배포 |
| Pydantic | [concepts/pydantic.md](concepts/pydantic.md) | 모델, BaseSettings, 검증 |
| WebSocket | [concepts/websocket.md](concepts/websocket.md) | 프로토콜, 메시지 타입 |

---

## 프로젝트

| 문서 | 경로 | 용도 |
|------|------|------|
| 개요 | [project/overview.md](project/overview.md) | 프로젝트 소개, 용어, WebSocket 프로토콜 |
| 시스템 아키텍처 | [project/architecture/system-design.md](project/architecture/system-design.md) | 레이어드 아키텍처, 의사결정 |
| 개발 계획 | [project/planning/development-plan.md](project/planning/development-plan.md) | 6주 개발 로드맵 |
| 향후 작업 | [project/planning/future-work-plan.md](project/planning/future-work-plan.md) | Phase별 작업, 우선순위 |
| 구현 상세 | [project/implementation/](project/implementation/) | project-structure, models, card-manager, game-manager, turn-manager, action-handler, websocket, best-practices |

---

## 운영

| 문서 | 경로 | 용도 |
|------|------|------|
| NAS 서버 구축 | [operations/nas-server-setup.md](operations/nas-server-setup.md) | 서버 환경, Nginx, SSL, CI/CD |
| 배포 체크리스트 | [operations/deployment-checklist.md](operations/deployment-checklist.md) | 배포 전 확인 사항 |
| 프론트엔드 연동 | [operations/frontend-coordination.md](operations/frontend-coordination.md) | WebSocket 프로토콜, 연동 가이드 |
| WebSocket 트러블슈팅 | [operations/websocket-troubleshooting.md](operations/websocket-troubleshooting.md) | 연결 문제 해결 |
| 데이터베이스 추천 | [operations/database-recommendation.md](operations/database-recommendation.md) | Redis, PostgreSQL |

---

## 변경 이력

| 문서 | 경로 |
|------|------|
| 2025-12-11 | [changelog/2025-12-11.md](changelog/2025-12-11.md) |
| 2025-12-12 | [changelog/2025-12-12.md](changelog/2025-12-12.md) |

---

## 에이전트 참조 가이드

- **FastAPI 라우트 추가 시**: concepts/fastapi.md, project/implementation/
- **게임 로직 수정 시**: project/implementation/ (game-manager, turn-manager, action-handler)
- **WebSocket 프로토콜 수정 시**: concepts/websocket.md, project/implementation/websocket.md
- **배포/운영 시**: operations/
