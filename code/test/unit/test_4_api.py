# Test rest-api server

from json import loads as json_loads
from base64 import b64encode
import pytest

from hado.api.server import api

from hado.core.config import shared

from .util import HTTP_CODES, check_methods
from .pseudo import PseudoConfig

# pylint: disable=W0621


@pytest.fixture
def app(mocker):
    mocker.patch('hado.api.get.shared', PseudoConfig)
    # mocker.patch('hado.api.post.shared', PseudoConfig)
    mocker.patch('hado.core.system.shared', PseudoConfig)
    return api


@pytest.fixture
def client(app):
    return app.test_client()


def auth() -> dict:
    c = b64encode(
        f"{shared.CONFIG_ENGINE['API_SYNC_USER']}:"
        f"{shared.CONFIG_ENGINE['API_SYNC_PWD']}".encode('utf-8')
    ).decode('utf-8')
    return {"Authorization": f"Basic {c}"}


class TestAPIStati:
    # todo: check that responses are not empty

    def test_basic_auth(self, client):
        rg = client.get('/', headers=auth())
        assert rg.status_code == HTTP_CODES['OK']
        assert rg.content_type == 'application/json'

    # I've found no working way of mocking values
    #   outside request-functions when using flask..
    #   basically when API_AUTH is set to false; auth will be optional
    # def test_no_auth(self, client):
    #     rg = client.get('/')
    #     assert rg.status_code == HTTP_CODES['OK']
    #     assert rg.content_type == 'application/json'

    def test_get_system(self, client):
        rg = client.get('/s', headers=auth())
        assert rg.status_code == HTTP_CODES['OK']
        assert rg.content_type == 'application/json'
        assert json_loads(rg.data) == PseudoConfig.TEST_SYSTEM.stats
        check_methods(p='/s', c=client)

    def test_get_resource(self, client):
        path = f'/a/TEST/r/{PseudoConfig.TEST_PLUGIN_R.name}'
        rg = client.get(path, headers=auth())
        assert rg.status_code == HTTP_CODES['OK']
        assert rg.content_type == 'application/json'
        assert json_loads(rg.data) == PseudoConfig.TEST_PLUGIN_R.stats
        check_methods(p=path, c=client)

    def test_get_monitoring(self, client):
        path = f'/a/TEST/m/{PseudoConfig.TEST_PLUGIN_M.name}'
        rg = client.get(path, headers=auth())
        assert rg.status_code == HTTP_CODES['OK']
        assert rg.content_type == 'application/json'
        assert json_loads(rg.data) == PseudoConfig.TEST_PLUGIN_M.stats
        check_methods(p=path, c=client)

    def test_get_whole(self, client):
        path = '/'
        rg = client.get(path, headers=auth())
        assert rg.status_code == HTTP_CODES['OK']
        assert rg.content_type == 'application/json'
        stats_apps = {'apps': {app.name: app.stats for app in PseudoConfig.CONFIG_LOADED['apps']}}
        stats_peers = {'peers': {}}
        assert json_loads(rg.data) == PseudoConfig.TEST_SYSTEM.stats | stats_apps | stats_peers
        check_methods(p=path, c=client)

    def test_get_sync(self, client):
        from hado.core.config.defaults import HARDCODED
        path = HARDCODED['API_SYNC_PATH']
        rg = client.get(path, headers=auth())
        assert rg.status_code == HTTP_CODES['OK']
        assert rg.content_type == 'application/json'
        stats_apps = {'apps': {app.name: app.stats for app in PseudoConfig.CONFIG_LOADED['apps']}}
        assert json_loads(rg.data) == PseudoConfig.TEST_SYSTEM.stats | stats_apps
        check_methods(p=path, c=client)

    def test_post_maintenance(self, client):
        path = '/c/m'
        rg = client.post(path, headers=auth())
        assert rg.status_code == HTTP_CODES['NI']
        check_methods(p=path, c=client, u='post')

    def test_post_standby(self, client):
        path = '/c/s'
        rg = client.post(path, headers=auth())
        assert rg.status_code == HTTP_CODES['NI']
        check_methods(p=path, c=client, u='post')

    def test_catch_all(self, client):
        r = client.get('/nonExistent')
        assert r.status_code == HTTP_CODES['NF']
        check_methods(p='/nonExistent', c=client)

    def test_get_allow_private(self, client):
        path = '/'
        rg = client.get(
            path,
            headers=auth(),
            environ_base={'REMOTE_ADDR': '192.168.111.111'}
        )
        assert rg.status_code == HTTP_CODES['OK']
        assert rg.content_type == 'application/json'

    def test_deny_public(self, client):
        path = '/'
        rg = client.get(path, headers=auth(), environ_base={'REMOTE_ADDR': '1.1.1.1'})
        assert rg.status_code == HTTP_CODES['D']

    def test_post_deny_nonlocal(self, client):
        path = '/c/s'
        rg = client.post(
            path,
            headers=auth(),
            environ_base={'REMOTE_ADDR': '192.168.111.111'}
        )
        assert rg.status_code == HTTP_CODES['D']
