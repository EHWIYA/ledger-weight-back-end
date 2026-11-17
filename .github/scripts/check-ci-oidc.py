"""GitHub OIDC와 NAS 전송 연결만 검사한다. 배포·SSH 인증·앱 요청은 하지 않는다."""
import base64
import json
import os
import socket
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request

CONFIG = {
    'EHWIYA/home-assistant-front-end': ('1243065308', 'deploy.yml', 'tag:iot-web-ci'),
    'EHWIYA/ledger-weight-back-end': ('1114418814', 'deploy-ledger-weight.yml', 'tag:ledger-ci'),
}
NAS = '100.88.40.125'


def identity(audience):
    url = os.environ['ACTIONS_ID_TOKEN_REQUEST_URL']
    request = urllib.request.Request(
        url + ('&' if '?' in url else '?') + urllib.parse.urlencode({'audience': audience}),
        headers={'Authorization': 'Bearer ' + os.environ['ACTIONS_ID_TOKEN_REQUEST_TOKEN']},
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.load(response)['value']


def exchange(client_id, jwt):
    request = urllib.request.Request(
        'https://api.tailscale.com/api/v2/oauth/token-exchange',
        data=urllib.parse.urlencode({'client_id': client_id, 'jwt': jwt}).encode(),
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            assert json.load(response).get('access_token'), 'Access token missing'
            return response.status
    except urllib.error.HTTPError as error:
        error.close()
        return error.code


def check_identity(repo, config):
    client_id, audience = os.environ['TS_OIDC_CLIENT_ID'], os.environ['TS_OIDC_AUDIENCE']
    assert client_id and audience, 'OIDC identifiers missing'
    jwt = identity(audience)
    part = jwt.split('.')[1]
    claims = json.loads(base64.urlsafe_b64decode(part + '=' * (-len(part) % 4)))
    expected = {'iss': 'https://token.actions.githubusercontent.com',
                'sub': 'repo:' + repo + ':ref:refs/heads/main', 'aud': audience,
                'repository_id': config[0], 'repository_owner_id': '150232499',
                'workflow_ref': repo + '/.github/workflows/' + config[1] + '@refs/heads/main',
                'ref': 'refs/heads/main'}
    assert all(claims.get(k) == v for k, v in expected.items()), 'OIDC claims mismatch'
    denied = exchange(client_id, identity(audience + '/invalid-audience-probe'))
    assert denied == 403, 'Wrong audience was not rejected as expected'
    accepted = exchange(client_id, jwt)
    assert accepted == 200, 'Authorized OIDC exchange failed'
    print(json.dumps({'identity_claims_match': True, 'wrong_audience_http': denied,
                      'authorized_exchange_http': accepted, 'tokens_saved': False}))


def check_transport(config):
    status = json.loads(subprocess.check_output(['tailscale', 'status', '--json'], timeout=15))
    assert status['BackendState'] == 'Running', 'Tailscale not running'
    assert status['Self'].get('Tags') == [config[2]], 'Unexpected CI tag identity'
    with socket.create_connection((NAS, 22), timeout=15) as connection:
        assert connection.recv(128).startswith(b'SSH-'), 'NAS SSH banner missing'
    pin = os.environ['NAS_SSH_HOST_KEYS']
    expected = {tuple(line.split()[1:3]) for line in pin.splitlines()
                if len(line.split()) >= 3 and line.split()[1] == 'ssh-ed25519'}
    assert len(expected) == 1, 'Pinned ed25519 host key missing or ambiguous'
    scan = subprocess.run(['ssh-keyscan', '-T', '10', '-t', 'ed25519', NAS],
                          capture_output=True, text=True, timeout=15)
    observed = {tuple(line.split()[1:3]) for line in scan.stdout.splitlines()
                if len(line.split()) >= 3 and not line.startswith('#')}
    assert scan.returncode == 0 and observed == expected, 'NAS SSH host key mismatch'
    try:
        connection = socket.create_connection((NAS, 443), timeout=4)
    except (TimeoutError, OSError):
        pass
    else:
        connection.close()
        raise AssertionError('Unexpected NAS TCP 443 access')
    print(json.dumps({'ci_tag_verified': True, 'nas_ssh_banner': True,
                      'nas_ssh_host_key_pinned': True, 'nas_tcp443_unreachable': True,
                      'ssh_authentication_or_command': False, 'app_requests': False}))


if __name__ == '__main__':
    repo = os.environ['GITHUB_REPOSITORY']
    config = CONFIG[repo]
    if sys.argv[1] == 'identity':
        check_identity(repo, config)
    elif sys.argv[1] == 'transport':
        check_transport(config)
    else:
        raise SystemExit('Unsupported check mode')
