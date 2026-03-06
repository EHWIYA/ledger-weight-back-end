# GitHub / Git 개념 (초보자용)

이 프로젝트의 Git·GitHub 워크플로우를 기준으로 설명합니다.

---

## 1. Git 기본

### 이게 뭔가요?
**버전 관리 시스템**입니다. 코드 변경 이력을 추적하고, 이전 상태로 되돌리거나 브랜치로 분기할 수 있습니다.

### 기본 명령어
- `git status` — 변경 파일 확인
- `git add <파일>` — 스테이징
- `git commit -m "메시지"` — 커밋
- `git push` — 원격 저장소에 푸시
- `git pull` — 원격에서 가져오기

---

## 2. 커밋 메시지 형식 (이 프로젝트)

### 형식
```
YYMMDD > back-end > fast-api > 작업내용 한줄 요약
```

### 예시
```
260306 > back-end > fast-api > docs 폴더 일원화 및 재구성
```

### 한글 인코딩
- PowerShell에서 한글 커밋 메시지 직접 전달 시 깨질 수 있음
- **해결**: `commit_message.txt` 파일에 메시지 작성 후 `git commit -F commit_message.txt` 사용

---

## 3. 브랜치

### 이 프로젝트
- **main**: 기본 배포 브랜치
- GitHub Actions가 `main` 푸시 시 자동 배포

---

## 4. GitHub Actions (CI/CD)

### 이게 뭔가요?
GitHub에서 **자동으로 스크립트를 실행**하는 기능입니다. main 푸시 시 Docker 이미지 빌드 → GHCR 푸시 → NAS 서버 SSH로 배포를 수행합니다.

### 이 프로젝트 워크플로우
- **파일**: `.github/workflows/deploy-ledger-weight.yml`
- **트리거**: `main` 브랜치 push
- **단계**:
  1. Docker 이미지 빌드
  2. GHCR( GitHub Container Registry)에 푸시
  3. Tailscale VPN 연결
  4. NAS 서버 SSH 접속
  5. `docker compose pull && docker compose up -d` 실행

### 필요한 Secrets
- `TS_AUTH_KEY` — Tailscale 인증 키
- `NAS_SERVER_USER` — SSH 사용자명
- `NAS_SERVER_SSH_KEY` — SSH 개인키
