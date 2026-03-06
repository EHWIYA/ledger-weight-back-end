# Docker 개념 (초보자용)

이 프로젝트의 Docker 사용 방식을 기준으로 설명합니다.

---

## 1. Docker란?

### 이게 뭔가요?
**컨테이너**로 애플리케이션을 패키징하고 실행하는 도구입니다. "이 환경에서만 돌아간다"는 문제를 해결하고, 개발·테스트·배포 환경을 동일하게 유지할 수 있습니다.

---

## 2. Dockerfile

### 이게 뭔가요?
**이미지를 만드는 레시피**입니다. 베이스 이미지, 설치할 패키지, 실행 명령을 정의합니다.

### 이 프로젝트
- **베이스**: Python 3.12-slim
- **포트**: 8088
- **실행**: `uvicorn app.main:app --host 0.0.0.0 --port 8088`

---

## 3. docker-compose

### 이게 뭔가요?
여러 컨테이너를 **한 번에 정의·실행**하는 도구입니다. 이 프로젝트는 단일 서비스만 사용합니다.

### 이 프로젝트 (`docker-compose.yml`)
```yaml
services:
  ledger-weight-api:
    image: ghcr.io/ehwiya/ledger-weight-back-end:latest
    ports:
      - "127.0.0.1:8088:8088"
    env_file:
      - .env
```

- **이미지**: GitHub Container Registry에서 `latest` 태그
- **포트**: 호스트 127.0.0.1:8088 → 컨테이너 8088 (Nginx 프록시용)
- **환경**: `.env` 파일 로드

---

## 4. 이미지 빌드 및 배포 흐름

1. **로컬**: 코드 수정 → Git push
2. **GitHub Actions**: Dockerfile로 이미지 빌드 → GHCR 푸시
3. **NAS 서버**: `docker compose pull` → 새 이미지 받기 → `docker compose up -d` → 재시작

---

## 5. 로컬에서 실행

```bash
# 이미지 빌드
docker build -t ledger-weight-api .

# 실행 (포트 8088)
docker run -p 8088:8088 --env-file .env ledger-weight-api
```

또는 docker-compose:
```bash
docker compose up -d
```
