# testing functions used to sync data between custer-nodes

# todo: fetcher different resource modes

from hado.core.config.defaults import ENGINE as ENGINE_DEFAULTS


class TestSync:
    def test_add_fetch_threads(self, mocker):
        from hado.util.threader import Loop
        from hado.core.peer import Peer
        from hado.core.switch.fetch import add_workers
        from .pseudo import PseudoPlugin, PseudoResource, PseudoConfig, PseudoApp

        p = Peer(
            name='TestPeer',
            host='127.0.0.1',
            port=ENGINE_DEFAULTS['DEFAULT_PEER_API_PORT'],
            auth=ENGINE_DEFAULTS['DEFAULT_PEER_AUTH'],
            user=ENGINE_DEFAULTS['DEFAULT_PEER_SYNC_USER'],
            pwd=ENGINE_DEFAULTS['DEFAULT_PEER_SYNC_PWD'],
        )
        PseudoConfig.CONFIG_LOADED['peers'].append(p)
        PseudoConfig.CONFIG_LOADED['apps'][0].peers.append(p)
        mocker.patch('hado.core.app.Monitoring', PseudoPlugin)
        mocker.patch('hado.core.app.Resource', PseudoResource)
        mocker.patch('hado.core.switch.fetch.shared', PseudoConfig)
        mocker.patch('hado.core.peer.shared', PseudoConfig)

        t = Loop()
        add_workers(threader=t)

        tl = [w.description for w in t.jobs]
        assert len(tl) == 5
        assert f"App '{PseudoApp.name}' resource '{PseudoConfig.TEST_PLUGIN_R.name}' - status check" in tl
        assert f"App '{PseudoApp.name}' resource '{PseudoConfig.TEST_PLUGIN_R.name}' - up check" in tl
        assert f"App '{PseudoApp.name}' monitoring '{PseudoConfig.TEST_PLUGIN_M.name}'" in tl
        assert f"Peer '{p.name}' sync" in tl
        assert f"System monitoring '{PseudoConfig.TEST_SYSTEM.monitoring[0].name}'" in tl
