# 장부의 무게 프로젝트 문서

이 디렉토리는 프로젝트의 모든 기술 문서를 포함합니다. docs와 logs를 일원화하여 관리합니다.

---

## 문서 구조

```
docs/
├── README.md              # 이 파일
├── INDEX.md               # 빠른 탐색 인덱스 (에이전트 참조 가이드 포함)
├── index.html             # 문서 대시보드 (서버 /docs-view/ 로 접근)
├── visual-guide/          # 시각화 가이드 (Mermaid 다이어그램)
├── concepts/              # 학습용 개념 (초보자급)
│   ├── python.md
│   ├── fastapi.md
│   ├── github-git.md
│   ├── docker.md
│   ├── pydantic.md
│   └── websocket.md
├── project/               # 프로젝트 문서
│   ├── overview.md
│   ├── architecture/
│   ├── planning/
│   └── implementation/
├── operations/            # 운영/배포
├── changelog/             # 날짜별 작업일지 (기존 logs 통합)
└── archive/               # 보관 문서
```

---

## 문서 대시보드 접근

서버 실행 후 다음 URL로 접속:

- **대시보드**: `http://localhost:8088/docs-view/`
- **시각화 가이드**: `http://localhost:8088/docs-view/visual-guide/index.html`
- **API 문서 (Swagger)**: `http://localhost:8088/docs`

---

## changelog (변경 이력)

기존 `logs/` 폴더의 날짜별 작업일지가 `docs/changelog/`로 통합되었습니다.

- **형식**: `changelog/YYYY-MM-DD.md`
- **내용**: 작업 시간, 완료/진행 작업, 이슈·해결, 다음 계획, 메모

---

## 에이전트 참조

- **INDEX.md**: 섹션별 경로, 키워드, 1줄 요약
- **참조 시점**: FastAPI 수정 → concepts/fastapi.md, project/implementation/
- **참조 시점**: 게임 로직 → project/implementation/
- **참조 시점**: 배포/운영 → operations/
