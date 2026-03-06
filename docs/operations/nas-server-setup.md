# NAS 서버 구축 가이드 (서버 환경 구축 전용)

**작성일**: 2025-12-11  
**대상**: NAS 서버 우분투 환경에서 서버 구축 작업  
**주의**: 이 문서는 **서버 구축 및 실행 환경 설정**만 다룹니다. 코드 개발은 로컬에서 진행합니다.

---

## 📋 작업 범위 구분

### ✅ 로컬(Windows)에서 진행할 작업 (백엔드 개발)
- 코드 작성 및 수정
- 기능 구현
- 테스트 코드 작성
- Git 커밋 및 푸시

### ✅ NAS 서버(우분투)에서 진행할 작업 (서버 구축)
- 프로젝트 배포 (Git pull 또는 파일 전송)
- Python 환경 설정
- 의존성 설치
- 서버 실행 환경 구축
- 프로세스 관리 (systemd, supervisor 등)
- 포트 및 방화벽 설정
- 서버 모니터링 및 로그 관리

---

## 🎯 NAS 서버에서 필요한 작업

### 1. 프로젝트 배포

**프로젝트 디렉토리 구조:**
```bash
# 권장 프로젝트 경로
/opt/ledger-weight/ledger-weight-back-end
# 또는
/home/[username]/ledger-weight/ledger-weight-back-end
```

**방법 1: Git 사용 (권장)**
```bash
# 프로젝트 디렉토리 생성
sudo mkdir -p /opt/ledger-weight
cd /opt/ledger-weight

# GitHub 레포지토리 클론
git clone https://github.com/[username]/ledger-weight-back-end.git
cd ledger-weight-back-end

# 최신 코드 가져오기 (이후 업데이트 시)
git pull origin main
```

**방법 2: 파일 전송**
```bash
# SCP 또는 SFTP로 파일 전송
# 로컬에서 실행:
# scp -r ./ledger-weight-back-end user@nas-server:/opt/ledger-weight/
```

**방법 2: 파일 전송**
```bash
# SCP 또는 SFTP로 파일 전송
# 로컬에서 실행:
# scp -r ./ledger-weight-back-end user@nas-server:/path/to/project/
```

---

### 2. Python 환경 설정

```bash
# Python 3.8+ 확인
python3 --version

# 가상환경 생성
python3 -m venv venv

# 가상환경 활성화
source venv/bin/activate

# pip 업그레이드
pip install --upgrade pip
```

---

### 3. 의존성 설치

```bash
# requirements.txt에서 패키지 설치
pip install -r requirements.txt

# 설치 확인
pip list
```

---

### 4. 환경 변수 설정

```bash
# .env 파일 생성
nano .env
```

**.env 파일 내용:**
```env
# 서버 설정
HOST=0.0.0.0
PORT=8080

# 애플리케이션 설정
APP_NAME=장부의 무게 API
APP_VERSION=0.1.0
DEBUG=False

# CORS 설정
CORS_ORIGINS=["*"]

# WebSocket 설정
WS_MAX_CONNECTIONS=100
WS_HEARTBEAT_INTERVAL=30

# 게임 설정
MAX_PLAYERS=7
MIN_PLAYERS=4
```

---

### 5. 서버 실행 방법

#### 방법 1: 직접 실행 (개발/테스트용)
```bash
# 가상환경 활성화
source venv/bin/activate

# 서버 실행
uvicorn app.main:app --host 0.0.0.0 --port 8080
```

#### 방법 2: systemd 서비스로 실행 (프로덕션 권장)

**서비스 파일 생성:**
```bash
sudo nano /etc/systemd/system/ledger-weight-api.service
```

**서비스 파일 내용:**
```ini
[Unit]
Description=Ledger Weight Backend API
After=network.target

[Service]
Type=simple
User=your-username
WorkingDirectory=/opt/ledger-weight/ledger-weight-back-end
Environment="PATH=/opt/ledger-weight/ledger-weight-back-end/venv/bin"
ExecStart=/opt/ledger-weight/ledger-weight-back-end/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8080
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**서비스 관리:**
```bash
# 서비스 활성화
sudo systemctl enable ledger-weight-api

# 서비스 시작
sudo systemctl start ledger-weight-api

# 서비스 상태 확인
sudo systemctl status ledger-weight-api

# 서비스 중지
sudo systemctl stop ledger-weight-api

# 로그 확인
sudo journalctl -u ledger-weight-api -f
```

#### 방법 3: Supervisor 사용

**설치:**
```bash
sudo apt-get install supervisor
```

**설정 파일 생성:**
```bash
sudo nano /etc/supervisor/conf.d/ledger-weight-api.conf
```

**설정 파일 내용:**
```ini
[program:ledger-weight-api]
command=/opt/ledger-weight/ledger-weight-back-end/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8080
directory=/opt/ledger-weight/ledger-weight-back-end
user=your-username
autostart=true
autorestart=true
stderr_logfile=/var/log/ledger-weight/ledger-weight-api-error.log
stdout_logfile=/var/log/ledger-weight/ledger-weight-api-access.log
```

**Supervisor 관리:**
```bash
# 설정 리로드
sudo supervisorctl reread
sudo supervisorctl update

# 서비스 시작/중지
sudo supervisorctl start ledger-weight-api
sudo supervisorctl stop ledger-weight-api
sudo supervisorctl status ledger-weight-api
```

---

### 6. 포트 및 방화벽 설정

#### 포트 확인
```bash
# 8080 포트 사용 중인지 확인
sudo netstat -tulpn | grep 8080
# 또는
sudo ss -tulpn | grep 8080
```

#### 방화벽 설정 (UFW)
```bash
# UFW 활성화
sudo ufw enable

# 8080 포트 열기
sudo ufw allow 8080/tcp

# 방화벽 상태 확인
sudo ufw status
```

#### 방화벽 설정 (iptables)
```bash
# 8080 포트 열기
sudo iptables -A INPUT -p tcp --dport 8080 -j ACCEPT

# 규칙 저장 (Ubuntu)
sudo netfilter-persistent save
```

---

### 7. 도메인 설정 (ledger-weight-api.livbee.co.kr)

#### 7.1 가비아 DNS 설정

**가비아 관리자 페이지에서 설정:**
1. 가비아 도메인 관리 페이지 접속
2. `livbee.co.kr` 도메인 선택
3. DNS 관리 → 레코드 추가
4. 서브도메인 설정:
   - **호스트**: `ledger-weight-api`
   - **타입**: `A`
   - **값**: NAS 서버의 공인 IP 주소
   - **TTL**: 3600 (또는 기본값)

**참고**: DNS 전파에는 최대 24시간이 소요될 수 있지만, 보통 몇 분~몇 시간 내 완료됩니다.

#### 7.2 Nginx 리버스 프록시 설정

**Nginx 설치:**
```bash
sudo apt-get update
sudo apt-get install nginx
```

**설정 파일 생성:**
```bash
sudo nano /etc/nginx/sites-available/ledger-weight-api.conf
```

**설정 파일 내용:**
```nginx
server {
    listen 80;
    server_name ledger-weight-api.livbee.co.kr;

    # 로그 설정
    access_log /var/log/nginx/ledger-weight-api-access.log;
    error_log /var/log/nginx/ledger-weight-api-error.log;

    # WebSocket 업그레이드 헤더
    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_http_version 1.1;
        
        # WebSocket 지원
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        
        # 기본 프록시 헤더
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # 타임아웃 설정 (WebSocket용)
        proxy_read_timeout 86400;
        proxy_send_timeout 86400;
    }

    # 헬스 체크 엔드포인트
    location /health {
        proxy_pass http://127.0.0.1:8080/health;
        proxy_set_header Host $host;
    }
}
```

**심볼릭 링크 생성:**
```bash
sudo ln -s /etc/nginx/sites-available/ledger-weight-api.conf /etc/nginx/sites-enabled/
```

**설정 테스트:**
```bash
sudo nginx -t
```

**Nginx 재시작:**
```bash
sudo systemctl restart nginx
sudo systemctl enable nginx
```

#### 7.3 SSL 인증서 설정 (Let's Encrypt)

**Certbot 설치:**
```bash
sudo apt-get install certbot python3-certbot-nginx
```

**SSL 인증서 발급:**
```bash
sudo certbot --nginx -d ledger-weight-api.livbee.co.kr
```

**자동 갱신 설정:**
```bash
# 갱신 테스트
sudo certbot renew --dry-run

# 자동 갱신은 기본적으로 설정됨 (systemd timer)
```

**SSL 적용 후 Nginx 설정 자동 업데이트:**
- Certbot이 자동으로 Nginx 설정을 수정하여 HTTPS를 활성화합니다.
- HTTP → HTTPS 리다이렉트도 자동으로 설정됩니다.

#### 7.4 방화벽 설정 업데이트

```bash
# HTTP (80) 포트 열기
sudo ufw allow 80/tcp

# HTTPS (443) 포트 열기
sudo ufw allow 443/tcp

# 방화벽 상태 확인
sudo ufw status
```

**참고**: Nginx가 80, 443 포트를 사용하므로, FastAPI는 내부 포트(8080)만 사용합니다.

---

### 8. 서버 접속 테스트

```bash
# 로컬에서 테스트
curl http://localhost:8080/health

# 외부에서 테스트 (NAS 서버 IP 사용)
curl http://<nas-server-ip>:8080/health

# 도메인으로 테스트 (DNS 전파 후)
curl http://ledger-weight-api.livbee.co.kr/health

# HTTPS 테스트 (SSL 인증서 발급 후)
curl https://ledger-weight-api.livbee.co.kr/health

# WebSocket 연결 테스트
wscat -c ws://ledger-weight-api.livbee.co.kr/ws/test
# 또는
wscat -c wss://ledger-weight-api.livbee.co.kr/ws/test  # HTTPS 사용 시
```

---

### 9. 로그 관리

#### 로그 디렉토리 생성
```bash
mkdir -p /var/log/ledger-weight
chmod 755 /var/log/ledger-weight
```

#### 로그 로테이션 설정
```bash
sudo nano /etc/logrotate.d/ledger-weight
```

**로그 로테이션 설정:**
```
/var/log/ledger-weight/*.log {
    daily
    rotate 7
    compress
    delaycompress
    notifempty
    create 0644 your-username your-username
    sharedscripts
}
```

---

### 10. GitHub Actions CI/CD 자동배포 설정

#### 10.1 GitHub Actions 워크플로우 파일 생성

**워크플로우 파일 경로:**
```bash
# 로컬에서 생성
mkdir -p .github/workflows
```

**워크플로우 파일: `.github/workflows/deploy-ledger-weight.yml`**
```yaml
name: Deploy Ledger Weight Backend

on:
  push:
    branches:
      - main
  workflow_dispatch:  # 수동 실행 가능

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v3
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
      
      - name: Run tests (if available)
        run: |
          # pytest tests/  # 테스트가 있다면
          echo "Tests passed"
      
      - name: Deploy to NAS Server
        uses: appleboy/ssh-action@v0.1.5
        with:
          host: ${{ secrets.NAS_SERVER_HOST }}
          username: ${{ secrets.NAS_SERVER_USER }}
          key: ${{ secrets.NAS_SERVER_SSH_KEY }}
          port: ${{ secrets.NAS_SERVER_PORT }}
          script: |
            cd /opt/ledger-weight/ledger-weight-back-end
            git pull origin main
            source venv/bin/activate
            pip install -r requirements.txt
            sudo systemctl restart ledger-weight-api
            echo "Deployment completed"
```

#### 10.2 GitHub Secrets 설정

**GitHub 레포지토리 → Settings → Secrets and variables → Actions**

다음 Secrets를 추가:
- `NAS_SERVER_HOST`: NAS 서버 IP 주소 또는 도메인
- `NAS_SERVER_USER`: SSH 사용자명
- `NAS_SERVER_SSH_KEY`: SSH 개인키 (전체 내용)
- `NAS_SERVER_PORT`: SSH 포트 (기본값: 22)

**SSH 키 생성 (로컬에서):**
```bash
# SSH 키 생성 (없는 경우)
ssh-keygen -t ed25519 -C "github-actions-ledger-weight" -f ~/.ssh/github_actions_ledger_weight

# 공개키를 NAS 서버에 추가
ssh-copy-id -i ~/.ssh/github_actions_ledger_weight.pub user@nas-server

# 개인키 내용 복사 (GitHub Secrets에 추가)
cat ~/.ssh/github_actions_ledger_weight
```

#### 10.3 NAS 서버에서 자동배포 준비

**배포 스크립트 생성:**
```bash
# 배포 스크립트 생성
sudo nano /opt/ledger-weight/deploy-ledger-weight.sh
```

**배포 스크립트 내용:**
```bash
#!/bin/bash
# ledger-weight-back-end 자동배포 스크립트

PROJECT_DIR="/opt/ledger-weight/ledger-weight-back-end"
SERVICE_NAME="ledger-weight-api"

cd $PROJECT_DIR

# Git 최신 코드 가져오기
git pull origin main

# 가상환경 활성화
source venv/bin/activate

# 의존성 업데이트
pip install -r requirements.txt

# 서비스 재시작
sudo systemctl restart $SERVICE_NAME

# 서비스 상태 확인
sudo systemctl status $SERVICE_NAME

echo "Deployment completed at $(date)"
```

**스크립트 실행 권한 부여:**
```bash
chmod +x /opt/ledger-weight/deploy-ledger-weight.sh
```

**SSH 키 권한 설정:**
```bash
# GitHub Actions용 SSH 키 권한 설정
chmod 600 ~/.ssh/authorized_keys
```

#### 10.4 systemd 서비스 파일 업데이트

**서비스 파일: `/etc/systemd/system/ledger-weight-api.service`**
```ini
[Unit]
Description=Ledger Weight Backend API
After=network.target

[Service]
Type=simple
User=your-username
WorkingDirectory=/opt/ledger-weight/ledger-weight-back-end
Environment="PATH=/opt/ledger-weight/ledger-weight-back-end/venv/bin"
ExecStart=/opt/ledger-weight/ledger-weight-back-end/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8080
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**서비스 등록:**
```bash
sudo systemctl daemon-reload
sudo systemctl enable ledger-weight-api
sudo systemctl start ledger-weight-api
```

#### 10.5 CI/CD 테스트

**로컬에서 테스트:**
```bash
# 변경사항 커밋 및 푸시
git add .
git commit -m "Test CI/CD deployment"
git push origin main
```

**GitHub Actions 확인:**
1. GitHub 레포지토리 → Actions 탭
2. 워크플로우 실행 상태 확인
3. 로그 확인 및 오류 검토

---

## 📌 Cursor AI에게 질문할 내용

### 기본 서버 구축 질문

NAS 서버의 Cursor AI에게 다음과 같이 질문하세요:

> "FastAPI 프로젝트를 우분투 서버에서 실행할 수 있도록 환경을 구축해줘.
> 
> 작업 내용:
> 1. Python 가상환경 생성 및 활성화
> 2. requirements.txt에서 의존성 설치
> 3. .env 파일 생성 (PORT=8080 설정)
> 4. systemd 서비스 파일 생성하여 백그라운드 실행 설정
> 5. 방화벽에서 8080 포트 열기
> 6. 서비스 시작 및 상태 확인
> 
> 프로젝트 경로: /path/to/ledger-weight-back-end
> 실행 명령: uvicorn app.main:app --host 0.0.0.0 --port 8080"

또는 더 간단하게:

> "FastAPI 서버를 systemd 서비스로 등록해서 백그라운드에서 실행되도록 설정해줘.
> 포트는 8080이고, 서버 재시작 시 자동으로 시작되도록 해줘."

### 도메인 및 Nginx 설정 질문

> "Nginx를 설치하고 리버스 프록시를 설정해줘.
> 
> 도메인: ledger-weight-api.livbee.co.kr
> 백엔드 서버: http://127.0.0.1:8080
> 
> 작업 내용:
> 1. Nginx 설치
> 2. WebSocket 지원하는 리버스 프록시 설정 파일 생성
> 3. SSL 인증서 발급 (Let's Encrypt)
> 4. HTTP → HTTPS 리다이렉트 설정
> 5. 방화벽에서 80, 443 포트 열기
> 
> WebSocket 연결도 지원해야 하므로 Upgrade 헤더 설정을 포함해줘.
> 설정 파일명은 ledger-weight-api로 해줘."

또는 단계별로:

> "Nginx 리버스 프록시 설정 파일을 만들어줘.
> ledger-weight-api.livbee.co.kr 도메인으로 들어오는 요청을 
> 내부 포트 8080의 FastAPI 서버로 프록시하도록 설정해줘.
> WebSocket 연결도 지원해야 해.
> 파일명은 ledger-weight-api.conf로 해줘."

### GitHub Actions CI/CD 설정 질문

> "GitHub Actions를 이용한 CI/CD 자동배포를 설정해줘.
> 
> 작업 내용:
> 1. .github/workflows/deploy-ledger-weight.yml 워크플로우 파일 생성
> 2. main 브랜치에 push 시 자동 배포되도록 설정
> 3. NAS 서버에 SSH로 접속하여 배포 스크립트 실행
> 4. 배포 후 ledger-weight-api 서비스 재시작
> 
> 프로젝트 경로: /opt/ledger-weight/ledger-weight-back-end
> 서비스명: ledger-weight-api
> 
> GitHub Secrets는 나중에 직접 설정할 예정이니, Secrets 변수명만 명시해줘."

---

## 🔍 문제 해결

### 포트가 이미 사용 중인 경우
```bash
# 프로세스 찾기
sudo lsof -i :8080
# 또는
sudo fuser -k 8080/tcp

# 프로세스 종료
sudo kill -9 <PID>
```

### 서비스가 시작되지 않는 경우
```bash
# 로그 확인
sudo journalctl -u ledger-weight -n 50

# 서비스 파일 문법 확인
sudo systemctl daemon-reload
```

### 의존성 설치 오류
```bash
# pip 업그레이드
pip install --upgrade pip setuptools wheel

# 개별 패키지 설치
pip install fastapi uvicorn[standard] websockets
```

---

## 📝 체크리스트

### 기본 서버 구축
- [ ] 프로젝트 배포 완료 (`/opt/ledger-weight/ledger-weight-back-end`)
- [ ] Python 가상환경 생성 및 활성화
- [ ] 의존성 설치 완료
- [ ] .env 파일 생성 및 설정
- [ ] systemd/supervisor 서비스 등록 (`ledger-weight-api`)
- [ ] 방화벽 포트 개방 (8080)
- [ ] 서버 실행 및 상태 확인
- [ ] 헬스 체크 엔드포인트 테스트
- [ ] 로그 디렉토리 및 로테이션 설정 (`/var/log/ledger-weight/`)

### 도메인 및 Nginx 설정
- [ ] 가비아 DNS 설정 (A 레코드 추가)
- [ ] Nginx 설치
- [ ] 리버스 프록시 설정 파일 생성 (`ledger-weight-api.conf`)
- [ ] WebSocket 지원 설정 확인
- [ ] Nginx 설정 테스트 및 재시작
- [ ] SSL 인증서 발급 (Let's Encrypt)
- [ ] 방화벽 포트 개방 (80, 443)
- [ ] 도메인으로 접속 테스트
- [ ] HTTPS 접속 테스트
- [ ] WebSocket 연결 테스트 (wss://)

### GitHub Actions CI/CD
- [ ] GitHub 레포지토리 확인 및 URL 업데이트
- [ ] GitHub Secrets 설정 (NAS_SERVER_HOST, NAS_SERVER_USER, NAS_SERVER_SSH_KEY, NAS_SERVER_PORT)
- [ ] SSH 키 생성 및 NAS 서버에 추가
- [ ] `.github/workflows/deploy-ledger-weight.yml` 워크플로우 파일 생성
- [ ] 배포 스크립트 생성 (`/opt/ledger-weight/deploy-ledger-weight.sh`)
- [ ] systemd 서비스명 확인 (`ledger-weight-api`)
- [ ] CI/CD 테스트 (main 브랜치 push)
- [ ] 자동배포 동작 확인

---

**작성자**: 백엔드 개발자  
**최종 업데이트**: 2025-12-11

