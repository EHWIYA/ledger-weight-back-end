# 에이전트 역할 기반 폴더 구조 제안 검토 보고서

**검토일**: 2025-03-04  
**대상**: ledger-weight-back-end (FastAPI/Python, WebSocket 카드 게임 서버)

---

## 1. 제안 요약

- **목표**: 에이전트가 “전체 코드를 다 읽지 않아도” **폴더 이름 + 파일 구성**만으로 역할을 인지하고, 해당 폴더의 `.cursorrules`/`README.md`로 **즉시 페르소나 전환**하여 작업할 수 있게 하는 구조.
- **핵심 전략**:  
  - 역할별 전용 폴더 (API / 코어 / 모델 / 서비스 / WebSocket / 스크립트 / 문서 / 테스트)  
  - `.cursor/rules/`로 **작업·폴더별 규칙 분리** (architect, database, tester 등)  
  - **컨텍스트 격리**: 폴더/파일 단위로 규칙 적용 → 토큰·속도 효율  
  - **active_context.md**로 “무엇을 했고, 다음은 무엇인가” 기록 → 다음 세션 연속성  
  - **파일당 ~100줄** 유지 → 수정 범위 축소, 에이전트 이해도·정확도 향상

---

## 2. 현재 프로젝트와의 매핑

| 제안 구조        | 현재 구조                    | 비고 |
|-----------------|-----------------------------|------|
| `src/api/`      | `app/api/`                  | 동일 역할. 라우팅/엔드포인트. |
| `src/core/`     | `app/config.py` + `app/utils/` | 설정·보안·공통 모듈을 core로 통합 가능. |
| `src/models/`   | `app/models/`               | 동일. DB·Pydantic 모델. |
| `src/services/` | **`app/game/`**             | 게임 매니저·카드·턴·액션 등 비즈니스 로직 → services에 대응. |
| `src/websocket/`| `app/websocket/`            | 동일. 실시간 연결·메시지 처리. |
| `scripts/`      | 없음                        | 배포·DB 초기화 등 스크립트용으로 신설 권장. |
| `docs/`         | `docs/`                     | 이미 존재. 문서 에이전트 전용. |
| `tests/`        | `tests/`                    | 이미 존재. QA/테스트 에이전트 전용. |
| `.cursor/rules/`| 없음                        | **신설 권장.** architect, database, tester 등 역할 규칙. |

- **이름 차이**: 제안은 `src/`, 현재는 `app/`.  
  - **옵션 A**: 그대로 `app/` 유지하고, 내부만 역할별로 정리 (api, core, models, services, websocket) + `.cursor/rules/`만 추가.  
  - **옵션 B**: `app` → `src` 리네이밍 후 제안 구조에 맞춤 (진입점·임포트 경로 전면 수정 필요).

---

## 3. 검토 의견

### 3.1 장점 (채택 권장 포인트)

1. **컨텍스트 격리**  
   - 폴더/규칙 단위로 “지금 무엇을 만지는지”가 명확해져, 에이전트가 불필요하게 전체 코드를 읽는 일을 줄일 수 있음.  
   - `src/websocket/` 수정 시 “실시간 멀티플레이어 로직” 규칙만 적용하는 식의 운영이 가능.

2. **.cursor/rules/ 분리**  
   - architect / database / tester 등 **작업 유형별 규칙**을 두면, Cursor의 “폴더/파일 기반 규칙”과 잘 맞음.  
   - 현재 프로젝트에는 `.cursor`가 없으므로, 여기부터 도입하는 것이 부담이 적고 효과가 큼.

3. **active_context.md**  
   - “방금 한 작업 + 다음 단계”를 짧게 유지하면, 세션 간 맥락 유지와 온보딩 비용 감소에 도움이 됨.  
   - 루트 또는 `docs/`에 두고, 에이전트 작업 종료 시 갱신하도록 규칙에 넣는 것을 권장.

4. **100줄 규칙**  
   - 이미 목표로 두고 계신다면, 서브 에이전트화(작은 단위 수정)와 잘 맞고, in-place 수정·이해도 향상에 유리함.

5. **scripts/ 신설**  
   - 배포·DB 초기화·도구 스크립트를 한곳에 두면 “자동화 에이전트” 역할을 부여하기 좋고, 현재 구조에서도 바로 추가 가능.

### 3.2 주의·보완 사항

1. **app vs src**  
   - `uvicorn app.main:app` 등 **진입점과 모든 `app.xxx` 임포트**가 이미 있으므로, `src`로 바꾸면 경로·테스트·CI 전반 수정이 필요함.  
   - **권장**: 우선은 **폴더 이름을 `app`으로 유지**하고, 내부를 역할별(`api`, `core`, `models`, `services`, `websocket`)로 정리 + `.cursor/rules/`·`active_context.md`·`scripts/`만 도입.  
   - 필요 시 나중에 `app` → `src` 마이그레이션을 별도 작업으로 진행.

2. **game/ → services/ 리네이밍**  
   - 의미적으로는 “게임 비즈니스 로직 = services”에 잘 맞음.  
   - 다만 `from app.game.xxx`를 쓰는 곳이 많으므로, 리네이밍 시 일괄 치환 및 테스트 실행이 필요함.

3. **core/ 구성**  
   - `config.py` + `utils/`(constants, validators 등)를 `app/core/`로 옮기면 “설정·공통” 역할이 분명해짐.  
   - 이동 시 `app.config` → `app.core.config`, `app.utils` → `app.core.utils` 등 임포트 경로만 정리하면 됨.

4. **제안된 mkdir 명령어 (Bash)**  
   - 제안 예시:  
     `mkdir -p .cursor/rules src/{api,core,models,services,websocket} docs tests scripts`  
   - Windows PowerShell에서는 `{api,core,...}` 확장이 동작하지 않음.  
   - 아래 “다음 단계”에 PowerShell용 명령 예시를 넣었음.

---

## 4. 추천 다음 단계 (우선순위)

- **1단계 (즉시, 구조만)**  
  - `.cursor/rules/` 생성.  
  - `scripts/` 생성.  
  - (선택) 루트에 `active_context.md` 생성.  
  - **PowerShell에서 폴더 생성 예시**  
    ```powershell
    New-Item -ItemType Directory -Force -Path .cursor/rules
    New-Item -ItemType Directory -Force -Path scripts
    # app은 유지하는 경우: app 내부 역할 폴더는 이미 api, models, game, websocket, utils 존재
    # active_context.md
    New-Item -ItemType File -Force -Path active_context.md
    ```

- **2단계 (규칙 도입)**  
  - `.cursor/rules/` 아래에  
    - `architect.md` — 전체 구조·설계·100줄 원칙  
    - `database.md` — DB 스키마·마이그레이션  
    - `tester.md` — 테스트 작성·실행·검증  
  - 필요 시 `api.md`, `websocket.md` 등 폴더별 규칙 추가.

- **3단계 (선택, 점진적 리팩터)**  
  - `app/utils/` + `app/config.py` → `app/core/` 통합.  
  - `app/game/` → `app/services/` 리네이밍 (임포트 및 테스트 정리).  
  - 이후 필요하면 `app` → `src` 마이그레이션 검토.

---

## 5. 결론

- **역할 기반 폴더 + .cursor/rules + active_context + 100줄** 제안은 현재 프로젝트에 **그대로 적용 가능**하고, 에이전트의 컨텍스트 격리와 효율 측면에서 **도입을 권장**합니다.  
- **실무적으로는**  
  - `app` 이름 유지 + **.cursor/rules/·scripts/·active_context.md** 먼저 도입하고,  
  - 그다음 `app` 내부를 **core / services** 등으로 정리하는 순서**를 추천합니다.  
- Bash용 `mkdir -p ... src/{api,...}` 명령은 **Windows에서는 PowerShell용 명령으로 대체**해 사용하는 것이 안전합니다.

이 문서는 제안 검토 결과를 정리한 보고서이며, 실제 적용 시에는 `docs/INDEX.md` 또는 `README.md`에 이 문서 링크를 두면 이후 “에이전트 폴더 전략” 참고용으로 활용할 수 있습니다.
