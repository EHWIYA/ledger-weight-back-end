# OIDC 연결 전환 단계

현재 main push와 workflow_dispatch는 OIDC 및 NAS 전송 연결만 검사한다. 앱 빌드, GHCR 게시, rsync, SSH 인증/명령, Compose, 배포/재시작을 수행하지 않는다. 기존 TS_AUTH_KEY와 NAS SSH secret은 보존하지만 이 workflow에서 사용하지 않는다.

권한은 이 저장소의 main과 정확한 배포 workflow, Auth Keys Write 및 CI 태그 tag:ledger-ci에 한정한다. NAS TCP 22만 허용하고 SSH 공개 호스트 키를 고정한다. 잘못된 audience는 거부돼야 한다. JWT/단기 access token은 출력/저장하지 않는다.

ledger의 기존 컨테이너/프로세스와 메모리 게임 상태는 보존한다. 연결 검사 성공을 실제 배포/재시작 승인으로 보지 않는다.

복구 자료는 HDD snapshot other-ci-oidc-connect-20261117에 있다. 인증 문제가 있으면 연결 workflow를 보류하고 OIDC 변경분만 검토 복구한다. 예전 workflow를 되살려 서비스 변경 명령을 실행하지 않는다. 실제 배포는 운영 경로·정비 차단·백업·상태 보존·복구를 별도 승인/검증한 뒤 구현한다.
