# Test rest-api server

from json import loads as json_loads
import pytest

from hado.api.server import api
from hado.core.system import System

from .util import HTTP_CODES, check_methods

# pylint: disable=W0621


class PseudoPlugin:
    def __init__(self, n: str):
        self.name = n
        self.status = True
        self.stats = {self.name: self.status}


class PseudoApp:
    # pylint: disable=R0902
    def __init__(self, r: list, m: list):
        self.name = 'TEST'
        self.resources = r
        self.monitoring = m
        self.status = True
        self.health = 69
        self.resource_health = 69
        self.monitoring_health = 69
        self.stats = {
            'status': self.status,
            'health': self.health,
            'health_res': self.resource_health,
            'health_mon': self.monitoring_health,
            'resources': {r.name: r.status for r in self.resources},
            'monitoring': {m.name: m.status for m in self.monitoring},
        }


TEST_PLUGIN_R = PseudoPlugin(n='TestRes1')
TEST_PLUGIN_M = PseudoPlugin(n='TestMon1')
TEST_SYSTEM = System(monitoring=[])


class PseudoConfig:
    CONFIG_LOADED = {
        'apps': [
            PseudoApp(
                r=[TEST_PLUGIN_R],
                m=[TEST_PLUGIN_M]
            )
        ],
        'system': TEST_SYSTEM,
        'peers': [],
    }


@pytest.fixture
def app(mocker):
    mocker.patch('hado.api.get.shared', PseudoConfig)
    mocker.patch('hado.core.system.shared', PseudoConfig)
    return api


@pytest.fixture
def client(app):
    return app.test_client()


class TestAPIStati:
    # todo: check that responses are not empty

    def test_get_system(self, client):
        rg = client.get('/s')
        assert rg.status_code == HTTP_CODES['OK']
        assert rg.content_type == 'application/json'
        assert json_loads(rg.data) == TEST_SYSTEM.stats
        check_methods(p='/s', c=client)

    def test_get_resource(self, client):
        path = f'/a/TEST/r/{TEST_PLUGIN_R.name}'
        rg = client.get(path)
        assert rg.status_code == HTTP_CODES['OK']
        assert rg.content_type == 'application/json'
        assert json_loads(rg.data) == TEST_PLUGIN_R.stats
        check_methods(p=path, c=client)

    def test_get_monitoring(self, client):
        path = f'/a/TEST/m/{TEST_PLUGIN_M.name}'
        rg = client.get(path)
        assert rg.status_code == HTTP_CODES['OK']
        assert rg.content_type == 'application/json'
        assert json_loads(rg.data) == TEST_PLUGIN_M.stats
        check_methods(p=path, c=client)

    def test_get_whole(self, client):
        path = '/'
        rg = client.get(path)
        assert rg.status_code == HTTP_CODES['OK']
        assert rg.content_type == 'application/json'
        assert json_loads(rg.data) == TEST_SYSTEM.stats | {
            'apps': {app.name: app.stats for app in PseudoConfig.CONFIG_LOADED['apps']},
        }
        check_methods(p=path, c=client)

    def test_post_maintenance(self, client):
        path = '/c/m'
        rg = client.post(path)
        assert rg.status_code == HTTP_CODES['NI']
        check_methods(p=path, c=client, u='post')

    def test_post_standby(self, client):
        path = '/c/s'
        rg = client.post(path)
        assert rg.status_code == HTTP_CODES['NI']
        check_methods(p=path, c=client, u='post')

    def test_catch_all(self, client):
        r = client.get('/nonExistent')
        assert r.status_code == HTTP_CODES['NF']
        check_methods(p='/nonExistent', c=client)
