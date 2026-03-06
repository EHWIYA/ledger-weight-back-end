# 장부의 무게 백엔드 — 프로덕션 이미지
# Python 3.12-slim, 포트 8088 (nginx·서버와 동일)

FROM node:20-slim AS docs-builder
WORKDIR /app/docs-app
COPY docs-app/package*.json ./
RUN npm ci --omit=dev
COPY docs-app/ .

RUN npm run build

FROM python:3.12-slim

WORKDIR /app

# 의존성만 먼저 설치 (레이어 캐시 활용)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 앱 코드 복사
COPY . .

# docs-app/dist 빌드 결과물 복사 (node_modules는 .dockerignore로 제외)
COPY --from=docs-builder /app/docs-app/dist docs-app/dist

# non-root 사용자로 실행 (권한 최소화)
RUN adduser --disabled-password --gecos "" appuser && chown -R appuser:appuser /app
USER appuser

# 앱은 settings.PORT를 사용. 기본 8088로 노출
ENV PORT=8088
EXPOSE 8088

# 비개발 모드로 실행 (reload 없음)
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT}"]
