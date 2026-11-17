# 격리 ledger 검증 준비

부모가 `nas-build-guard/workload.py --kind build` 및 pytest에 `nas-test-guard/guard.py --timeout`을 적용해 실제 실행한다. 이 디렉터리의 파일은 준비물이며 자체적으로 검사 통과를 뜻하지 않는다. 모든 저장소 수정은 격리 checkout에만 있다.

## 후보 이미지

이미지 소스에 검증 harness가 섞이지 않도록 `git archive HEAD`를 별도 HDD 빈 디렉터리에 풀어 그 디렉터리를 Docker build context로 쓴다. HEAD는 `28d965a81e3095dd2e20eb5b035f8f611b7379ff`인지 먼저 확인한다. 빌드 중 base image/패키지 다운로드가 발생할 수 있으며, 기존 이미지·볼륨은 지우거나 교체하지 않는다. 고유한 로컬 후보 태그를 사용하고 push하지 않는다.

```bash
set -euo pipefail
repo=/mnt/HDD500GB/backups/managed/staging/ci-build-isolation-20261117/ledger
context=/mnt/HDD500GB/backups/managed/staging/ci-build-isolation-20261117/ledger-build-context
test "$(git -C "$repo" rev-parse HEAD)" = 28d965a81e3095dd2e20eb5b035f8f611b7379ff
mkdir "$context"
git -C "$repo" archive HEAD | tar -x -C "$context"
python3 /home/iwh/scripts/nas-build-guard/workload.py --kind build -- docker build -t ledger-ci-isolation:20261117 "$context"
```

빌드 실패를 수정 없이 원본과 함께 남긴다. Dockerfile의 `docs-app`은 빌드 시 생성한다. 위 build가 통과한 뒤 아래는 후보 이미지의 Python/FastAPI 코드에 대해 stdin으로만 주입하는 합성 ASGI 시험이다. publish port·bind mount·volume·운영 환경값을 전달하지 않으며 network none, read-only FS다. 동작 결과는 API ASGI 메시지 흐름을 시험한 것으로 실 TCP/TLS 또는 운영 WebSocket 재연결 검증은 아니다.

```bash
docker run --rm -i --network none --read-only --cap-drop ALL --security-opt no-new-privileges --pids-limit 128 --memory 512m -e PYTHONDONTWRITEBYTECODE=1 --entrypoint python ledger-ci-isolation:20261117 - < /mnt/HDD500GB/backups/managed/staging/ci-build-isolation-20261117/ledger/verification/synthetic_asgi.py
```

합성 플레이어 두 명의 참가와 개인 카드 숨김, disconnect 후 같은 프로세스 상태 지속, 단순 소켓 재연결과 기존 플레이어 재참가 거부, 별도 새 프로세스의 게임 부재를 검증한다. 실패하면 실제 출력과 종료 코드를 보존하고 허용 범위를 임의로 완화하지 않는다. 이 테스트는 게임 상태 무손실 이전 구현이나 운영 프로세스와 main의 일치 여부를 증명하지 않는다.

## 저장소 기존 CI

격리 checkout에 Python 3.12 venv를 만들고 `requirements.txt`와 테스트 전용 `verification/test-requirements.txt`를 설치한다. main의 앱 import 시 `docs-app/dist`가 필요하므로 먼저 격리 checkout의 docs-app에서 `npm ci --omit=dev` 및 `npm run build`를 가드 아래 완료해야 한다. npm/Python 다운로드와 빌드는 운영 호스트 설정을 수정하지 않는 격리 경로에서 실행한다.

- lint: `ruff check app tests`. 기존 CI는 별도로 최신 ruff를 설치하고, requirements에는 0.1.6이 고정되어 있으므로 사용한 버전을 보고한다.
- typing: `mypy app --ignore-missing-imports`. CI는 `|| true`라 통과 차단이 아니므로 실제 종료 코드와 경고를 별도로 기록한다.
- tests: `pytest tests -v`, NAS 테스트 가드 아래 최대 시간을 설정한다. TestClient에 필요한 `httpx==0.25.2`는 운영 의존성 파일을 바꾸지 않는 테스트 전용이다.

운영용 컨테이너 이름, 포트, 환경, 마운트, 게임 상태, WebSocket에 접속하지 않는다. CPU·메모리·디스크 여유는 각 빌드 직전 NAS guard가 확인하며 병렬 빌드는 금지한다. 정확한 빌드 시간은 부모가 실측한다.
