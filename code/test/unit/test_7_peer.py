# Test functionality of the service-object

from hado.core.config import shared
from hado.core.peer import Peer
from hado.core.config.defaults import ENGINE as ENGINE_DEFAULTS

from .util import capsys_error
from .pseudo import PseudoAPI

WAIT = 0.2


class TestPeer:
    def test_peer_sync_unreachable(self, capsys):
        p = Peer(
            name='TestPeer',
            host='127.0.0.1',
            port=ENGINE_DEFAULTS['DEFAULT_PEER_API_PORT'],
            auth=ENGINE_DEFAULTS['DEFAULT_PEER_AUTH'],
            user=ENGINE_DEFAULTS['DEFAULT_PEER_SYNC_USER'],
            pwd=ENGINE_DEFAULTS['DEFAULT_PEER_SYNC_PWD'],
        )

        assert p.up is None
        assert p.last_seen is None
        assert not p.is_up

        p.fetch()
        stdout, _ = capsys.readouterr()
        capsys_error(stdout)

        assert p.last_sync is None
        assert p.last_change is None
        assert p.last_data is None
        assert len(p.data_history) == 0

    def test_peer_sync_error_code(self, capsys):
        # api should return bad status code as loaded config is invalid
        p = Peer(
            name='TestPeer',
            host='127.0.0.1',
            port=ENGINE_DEFAULTS['DEFAULT_PEER_API_PORT'],
            auth=ENGINE_DEFAULTS['DEFAULT_PEER_AUTH'],
            user=ENGINE_DEFAULTS['DEFAULT_PEER_SYNC_USER'],
            pwd=ENGINE_DEFAULTS['DEFAULT_PEER_SYNC_PWD'],
        )

        assert p.up is None
        assert p.last_seen is None
        assert not p.is_up

        api = PseudoAPI()
        api.start()
        try:
            assert p.is_up

            p.fetch()
            stdout, _ = capsys.readouterr()
            capsys_error(stdout)

            assert p.last_sync is None
            assert p.last_change is None
            assert p.last_data is None
            assert len(p.data_history) == 0

        except AssertionError as e:
            api.stop()
            del api
            raise AssertionError(e)

        api.stop()
        del api

    def test_peer_sync_invalid_creds(self, capsys):
        # api should return bad status code as peer could not authenticate
        p = Peer(
            name='TestPeer',
            host='127.0.0.1',
            port=ENGINE_DEFAULTS['DEFAULT_PEER_API_PORT'],
            auth=ENGINE_DEFAULTS['DEFAULT_PEER_AUTH'],
            user='invalid',
            pwd='invalid',
        )

        assert p.up is None
        assert p.last_seen is None
        assert not p.is_up

        api = PseudoAPI()
        api.start()
        try:
            assert p.is_up

            p.fetch()
            stdout, _ = capsys.readouterr()
            capsys_error(stdout)

            assert p.last_sync is None
            assert p.last_change is None
            assert p.last_data is None
            assert len(p.data_history) == 0

        except AssertionError as e:
            api.stop()
            del api
            raise AssertionError(e)

        api.stop()
        del api

    def test_peer_sync(self, mocker):
        from hado.core.app import App
        from hado.core.system import System
        from .pseudo import PseudoPlugin, PseudoResource
        mocker.patch('hado.core.app.Monitoring', PseudoPlugin)
        mocker.patch('hado.core.app.Resource', PseudoResource)

        a = App(name='A', app={
            'peers': [],
            'resources': {'AppRes1': {}},
            'monitoring': {'AppMon1': {'vital': False}}
        })
        a.init_resources()

        shared.CONFIG_LOADED = {
            'apps': [a],
            'system': System(monitoring=[
                PseudoPlugin(name='SystemMon', config={})
            ])
        }

        _system = shared.CONFIG_LOADED['system'].stats
        _apps = {'apps': {app.name: app.stats for app in shared.CONFIG_LOADED['apps']}}
        compare = _system | _apps

        p = Peer(
            name='TestPeer',
            host='127.0.0.1',
            port=ENGINE_DEFAULTS['DEFAULT_PEER_API_PORT'],
            auth=ENGINE_DEFAULTS['DEFAULT_PEER_AUTH'],
            user=ENGINE_DEFAULTS['DEFAULT_PEER_SYNC_USER'],
            pwd=ENGINE_DEFAULTS['DEFAULT_PEER_SYNC_PWD'],
        )

        assert p.up is None
        assert p.last_seen is None
        assert not p.is_up
        api = PseudoAPI()
        api.start()
        try:
            assert p.is_up
            assert p.last_seen is not None

            assert p.last_sync is None
            assert p.last_change is None
            assert p.last_data is None
            assert len(p.data_history) == 0
            p.fetch()
            assert p.last_sync is not None
            assert p.last_change is not None
            assert p.last_data is not None
            assert len(p.data_history) == 1
            assert list(p.data_history.values())[0] == compare

        except AssertionError as e:
            api.stop()
            del api
            raise AssertionError(e)

        api.stop()
        del api
