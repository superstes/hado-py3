# Test rest-api server

import pytest

from hado.api.server import api

from .util import HTTP_CODES, check_methods

# pylint: disable=W0621


class PseudoPlugin:
    def __init__(self, n: str):
        self.name = n
        self.status = True


class PseudoApp:
    def __init__(self, r: list, m: list):
        self.name = 'TEST'
        self.resources = r
        self.monitoring = m
        self.status = True
        self.health = 69
        self.resource_health = 69
        self.monitoring_health = 69


TEST_PLUGIN = 'TestPlug'
TEST_CONFIG = {
    'apps': [
        PseudoApp(
            r=[PseudoPlugin(n=TEST_PLUGIN)],
            m=[PseudoPlugin(n=TEST_PLUGIN)]
        )
    ],
    'system': None, 'peers': [],
}


@pytest.fixture
def app(mocker):
    mocker.patch('hado.api.get.CONFIG_LOADED', TEST_CONFIG)

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
        check_methods(p='/s', c=client)

    def test_catch_all(self, client):
        r = client.get('/nonExistent')
        assert r.status_code == HTTP_CODES['NF']
        check_methods(p='/nonExistent', c=client)

    def test_get_resource(self, client):
        path = f'/a/TEST/r/{TEST_PLUGIN}'
        rg = client.get(path)
        assert rg.status_code == HTTP_CODES['OK']
        assert rg.content_type == 'application/json'
        check_methods(p=path, c=client)

    def test_get_monitoring(self, client):
        path = f'/a/TEST/m/{TEST_PLUGIN}'
        rg = client.get(path)
        assert rg.status_code == HTTP_CODES['OK']
        assert rg.content_type == 'application/json'
        check_methods(p=path, c=client)

    def test_get_whole(self, client):
        path = '/'
        rg = client.get(path)
        assert rg.status_code == HTTP_CODES['OK']
        assert rg.content_type == 'application/json'
        check_methods(p=path, c=client)
