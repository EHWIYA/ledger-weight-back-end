# 배포 전 확인 사항 및 체크리스트

**작성일**: 2025-12-11  
**최종 업데이트**: 2025-12-12  
**대상**: 서버 담당자

---

## 개요

서버 담당자에게 전달하기 전 확인할 사항과 배포 전 답변 보고서를 통합한 문서입니다.

---

## 완료된 사전 작업

1. `.env.example` 파일 생성 (`env.example`)
2. `README.md` 업데이트 (프로젝트 개요 및 빠른 시작 가이드)
3. `.gitignore` 확인 (`.env` 제외)
4. 로비 엔드포인트 `/lobby/{game_id}` 구현 완료 (2025-12-12)

---

## 확인 사항 답변

### 1. 프로젝트 레포지토리
- **GitHub URL**: 확인 후 `[username]` 업데이트 필요
- **브랜치**: `main`
- **권장**: Private + GitHub Actions Secrets

### 2. 필수 파일
- `requirements.txt`: 존재 및 최신
- `app/main.py`: 존재
- `.env`: 서버에서 별도 생성 (env.example 참고)

### 3. 환경 변수
| 변수명 | 기본값 | 설명 |
|--------|--------|------|
| HOST | 0.0.0.0 | 서버 호스트 |
| PORT | 8088 | 서버 포트 (가이드: 8088) |
| CORS_ORIGINS | ["*"] | CORS 허용 |
| WS_MAX_CONNECTIONS | 100 | 최대 WebSocket 연결 |
| MIN_PLAYERS | 4 | 최소 플레이어 수 |
| MAX_PLAYERS | 7 | 최대 플레이어 수 |

### 4. 실행 명령어
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8088
```

### 5. 엔드포인트
- `/health`: 헬스 체크
- `/lobby/{game_id}`: 로비 WebSocket
- `/ws/{player_id}`: WebSocket (호환용)

---

## 배포 체크리스트

### 기본
- [ ] 프로젝트 배포 완료
- [ ] Python 가상환경 및 의존성 설치
- [ ] .env 파일 생성
- [ ] 서비스 등록 (systemd/docker)
- [ ] 헬스 체크 테스트

### Docker 배포 (권장)
- [ ] docker-compose.yml 배치
- [ ] .env 파일 설정
- [ ] `docker compose pull && docker compose up -d`

---

## 전달 문서

1. [NAS 서버 구축 가이드](nas-server-setup.md)
2. `env.example`
3. `requirements.txt`
4. `README.md`

---

## 관련 문서

- [프론트엔드 연동](frontend-coordination.md)
- [WebSocket 트러블슈팅](websocket-troubleshooting.md)
