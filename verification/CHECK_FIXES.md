# 검사 오류 수정과 검증

기존 main의 Ruff 15건, mypy 40건을 타입 명확화·기존 모델 기본값의 명시 인자·미사용 import 정리와 누락 구성요소 오류 응답으로 수정했다. Role의 중복 내부 import로 남았던 첫 후보 Ruff 1건도 수정했다. 원래 default 값과 카드 공개/비공개 표현은 보존하며 비정상 요청의 오류 우선순위 및 BaseException 전파는 달라질 수 있다.

고정 최종 후보 이미지에서 Ruff 0건, mypy 0건, pytest 6개(기존2/추가4), 합성 ASGI 게임/WS 검증을 통과했다. 같은 추가 테스트를 기존 이미지에 적용하면 누락 플레이어/카드관리자 2개가 실패하며 원본 실패를 별도 보존했다. 기존 CI mypy 명령의 `|| true`를 제거해 미래 오류를 숨기지 않도록 했다. OIDC 배포 workflow는 그대로다.

Docker/ASGI 테스트는 운영 env·host mount·호스트 포트 없이 network none/read-only로 실행했다. 운영 ledger 컨테이너/메모리를 읽거나 바꾸지 않았다. 새 프로세스의 게임 부재/재연결 한계는 그대로이며, 이 수정은 상태 영속화/무손실 배포 구현이 아니다. 운영 교체는 계속 보류한다.

GitHub 테스트 job은 runner에서 문서 앱을 빌드하고 별도 테스트 의존성(httpx)을 설치한다. Ruff는 NAS에서 검증한 0.1.6으로 고정하고, pytest와 별도로 합성 ASGI 검사를 실행한다. 권한은 저장소 읽기로 제한한다. 이는 CI 변경안이며 실제 GitHub runner 통과를 뜻하지 않는다.

변경은 별도 HDD checkout과 patch에 보관하며 commit/push하지 않았다. 실제 GitHub runner 결과, 전체 공격/턴 조합과 운영 반영은 미검증이다. Pydantic 기존 deprecation warning 7개와 mypy의 untyped 함수 검사 범위 한계를 보고서에 남긴다.
