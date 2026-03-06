# 시각화 가이드 사용법

## 보는 방법

- **권장**: FastAPI 서버 실행 후 접속

  ```bash
  uvicorn app.main:app --host 0.0.0.0 --port 8088
  ```
  브라우저에서 **http://localhost:8088/docs-view/** 로 문서 대시보드에 접속한 뒤 "시각화 가이드 열기"를 클릭하거나,  
  **http://localhost:8088/docs-view/visual-guide/index.html** 로 직접 접속하세요.

- **대안**: 프로젝트 루트에서 `python -m http.server 8000` 실행 후 `http://localhost:8000/docs/visual-guide/index.html` 접속

- 또는 `index.html` 파일을 더블클릭해서 열 수 있으나, 일부 환경에서는 CDN 스크립트 로드가 막혀 다이어그램이 안 그려질 수 있습니다.

## 포함 내용

- **프로젝트 개요** — 서버·클라이언트 관계 다이어그램
- **프로젝트 구조** — `app` 패키지 디렉터리·파일 역할·의존 관계
- **HTTP 요청 흐름** — `/`, `/health` 요청의 시퀀스
- **WebSocket 메시지 흐름** — 로비 접속·참가·메시지 루프 시퀀스
- **Python 개념** — async, 타입 힌트, Enum, 클래스 등과 프로젝트 내 사용처
- **FastAPI 개념** — 앱·라우트·미들웨어·WebSocket·Query와 사용처
- **라이브러리 활용** — requirements.txt 기준 각 라이브러리 역할·사용 위치

초보자가 한 번에 구조·흐름·개념을 파악할 수 있도록 구성되어 있습니다.
