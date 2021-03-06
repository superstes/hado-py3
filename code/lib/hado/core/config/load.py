# checking config for errors, applying inheritance, converting to objects

from hado.util.debug import log
from hado.core.config.validate import validate
from hado.core.config.defaults import HARDCODED
from hado.core.app import App
from hado.core.plugin.monitoring import SystemMonitoring
from hado.core.system import System
from hado.util.helper import value_exists
from hado.core.plugin.util import existing_plugins, max_plugin_args, enough_args, supported_mode
from hado.core.config.util import valid_host
from hado.core.peer import Peer


class DeserializeConfig:
    def __init__(self, config_ha: dict, config_engine: dict):
        # note: not using global vars as this makes testing easier
        self.CONFIG_HA = config_ha
        self.CONFIG_ENGINE = config_engine
        self.LOADED = {
            'apps': [],
            'system': System(monitoring=[]),
            'peers': []  # global peers
        }
        self.PLUGINS = existing_plugins()

    def get(self) -> dict:
        if not self._check_engine():
            log('Got invalid engine config - exiting!')
            raise ValueError

        if not self._check_ha():
            log('Got invalid HA config - exiting!')
            raise ValueError

        self._get_apps()
        self._get_peers()
        self._get_system()
        return self.LOADED

    def _get_apps(self):
        for name, app in self.CONFIG_HA['apps'].items():
            if self._check_app(name=name, app=app):
                _a = App(name=name, app=app)
                _a.init_resources()
                self.LOADED['apps'].append(_a)

        if not value_exists(data=self.LOADED, key='apps'):
            log('No app could be loaded - exiting!')
            raise ValueError

    def _get_peers(self):
        # init peer objects and link them to apps
        _processed = []
        gp = []

        def add(_n: str, _p: dict) -> Peer:
            po = Peer(
                name=_n,
                host=_p['host'],
                port=_p['port'] if 'port' in _p else self.CONFIG_ENGINE['DEFAULT_PEER_API_PORT'],
                auth=_p['auth'] if 'auth' in _p else self.CONFIG_ENGINE['DEFAULT_PEER_AUTH'],
                user=_p['user'] if 'user' in _p else self.CONFIG_ENGINE['DEFAULT_PEER_SYNC_USER'],
                pwd=_p['pwd'] if 'pwd' in _p else self.CONFIG_ENGINE['DEFAULT_PEER_SYNC_PWD'],
            )
            self.LOADED['peers'].append(po)
            return po

        if value_exists(data=self.CONFIG_HA, key='peers', vt=dict):
            for n, p in self.CONFIG_HA['peers'].items():
                gp.append(add(_n=n, _p=p))
                _processed.append(n)

        for name, app in self.CONFIG_HA['apps'].items():
            ao = None
            for ao in self.LOADED['apps']:
                if ao.name == name:
                    ao.peers = gp
                    break

            if ao is None:
                log(f"App '{name}' was not initialized!")
                continue

            if value_exists(data=app, key='peers', vt=dict):
                for n, p in app['peers'].items():
                    if n not in _processed:
                        _processed.append(n)
                        ao.peers.append(add(_n=n, _p=p))

    def _get_system(self):
        if value_exists(data=self.CONFIG_HA, key='system', vt=dict) and \
                value_exists(data=self.CONFIG_HA['system'], key='monitoring', vt=dict):
            sys_mon_ok = True
            sys_mon = []
            for name, mon in self.CONFIG_HA['system']['monitoring'].items():
                if not self._check_monitoring(name=name, mon=mon, sys=True):
                    sys_mon_ok = False

                else:
                    sys_mon.append(SystemMonitoring(name=name, config=mon))

            if not sys_mon_ok:
                log(f"System - found config error in monitoring!")
                raise ValueError

            self.LOADED['system'].monitoring = sys_mon

    def _check_engine(self) -> bool:
        ok = True

        for s, v in self.CONFIG_ENGINE.items():
            if not validate(item=s, data=v):
                log(f"Engine has an invalid '{s}' configured - valid: '{validate(s)}'!")
                ok = False

        return ok

    def _check_ha(self) -> bool:
        if not value_exists(data=self.CONFIG_HA, key='apps', vt=dict):
            log("No valid 'apps' config found - exiting!")
            return False

        if not value_exists(data=self.CONFIG_HA, key='system', vt=dict):
            log(
                "No valid 'system' config found - using defaults and skipping system health monitoring!",
                lv=2
            )

        elif not value_exists(data=self.CONFIG_HA['system'], key='monitoring', vt=dict):
            log(
                "No valid 'system.monitoring' config found - skipping system health monitoring!",
                lv=2
            )

        if not value_exists(data=self.CONFIG_HA, key='peers', vt=dict):
            log(
                "No valid global 'peers' config found!",
                lv=2
            )

        else:
            for n, p in self.CONFIG_HA['peers'].items():
                if not self._check_peer(name=n, peer=p):
                    log(f"Global peer '{n}' has an invalid config!")
                    return False

        return True

    def _check_app(self, name: str, app: dict) -> bool:
        # pylint: disable=R0912
        log(f"Checking config for app '{name}'.", lv=3)

        if not value_exists(data=app, key='peers', vt=dict):
            log(f"App '{name}' has no valid peers configured!", lv=2)
            if not value_exists(data=self.CONFIG_HA, key='peers', vt=dict):
                log(f"App '{name}' neither app-specific nor global peers are configured!")
                return False

        if not value_exists(data=app, key='resources', vt=dict):
            log(f"App '{name}' has no valid resources configured!")
            return False

        if not value_exists(data=app, key='monitoring', vt=dict):
            log(f"App '{name}' has no valid app-specific monitoring configured.", lv=3)

        resources_ok = True
        monitoring_ok = True
        peers_ok = True

        for n, r in app['resources'].items():
            if not self._check_resource(name=n, res=r):
                resources_ok = False

        if value_exists(data=app, key='peers', vt=dict):
            for n, p in app['peers'].items():
                if not self._check_peer(name=n, peer=p):
                    peers_ok = False

        if value_exists(data=app, key='monitoring', vt=dict):
            for n, m in app['monitoring'].items():
                if not self._check_monitoring(name=n, mon=m):
                    monitoring_ok = False

        if not resources_ok:
            log(f"App '{name}' - found config error in resources!")

        if not peers_ok:
            log(f"App '{name}' - found config error in peers!")

        if not monitoring_ok:
            log(f"App '{name}' - found config error in monitoring!")

        if not monitoring_ok or not peers_ok or not resources_ok:
            return False

        log(f"App '{name}' - config checks passed!", lv=3)
        return True

    def _check_resource(self, name: str, res: dict) -> bool:
        if not value_exists(data=res, key='plugin'):
            log(f"Resource '{name}' has no plugin configured!")
            return False

        elif res['plugin'] not in self.PLUGINS['resource']:
            log(
                f"Resource '{name}' has an non-existent plugin configured - "
                f"not found in: '{HARDCODED['PATH_PLUGIN']}/resource'!"
            )
            return False

        plugin = res['plugin']
        if not value_exists(data=res, key='plugin_args'):
            if max_plugin_args(t='resource', p=plugin) != 0:
                log(f"Resource '{name}' has required plugin-arguments not configured!")
                return False

            log(f"Resource '{name}' has no plugin-arguments configured!", lv=3)

        else:
            if not enough_args(args=res['plugin_args'], t='resource', p=plugin):
                log(f"Resource '{name}' has too few plugin-arguments configured!")
                return False

        if not value_exists(data=res, key='vital'):
            log(
                f"Resource '{name}' has no vitality configured - "
                f"using default: '{self.CONFIG_ENGINE['DEFAULT_RESOURCE_VITAL']}'!",
                lv=3
            )

        if not value_exists(data=res, key='on_failure'):
            log(
                f"Resource '{name}' has no on_failure-action configured - "
                f"using default: '{self.CONFIG_ENGINE['DEFAULT_ACTION_FAILURE']}'!",
                lv=4
            )

        elif res['on_failure'] not in HARDCODED['ACTION']['VALID']:
            log(f"Resource '{name}' has an invalid on_failure-action configured!")
            return False

        if not value_exists(data=res, key='on_shutdown'):
            log(
                f"Resource '{name}' has no on_shutdown-action configured - "
                f"using default: '{self.CONFIG_ENGINE['DEFAULT_ACTION_FAILURE']}'!",
                lv=4
            )

        elif res['on_shutdown'] not in HARDCODED['ACTION']['VALID']:
            log(f"Resource '{name}' has an invalid on_shutdown-action configured!")
            return False

        if not value_exists(data=res, key='mode'):
            log(
                f"Resource '{name}' has no cluster-mode configured - "
                f"using default: '{self.CONFIG_ENGINE['DEFAULT_RESOURCE_MODE']}'!",
                lv=4
            )

        else:
            return self._check_resource_mode(res=res, name=name, plugin=plugin)

        return True

    @staticmethod
    def _check_resource_mode(res: dict, name: str, plugin: str) -> bool:
        # mode alias-translation and validation
        m = res['mode']
        if m in HARDCODED['MODE']['ALIAS']:
            res['mode'] = HARDCODED['MODE']['ALIAS'][m]

        if not validate(item='DEFAULT_RESOURCE_MODE', data=res['mode']):
            log(
                f"Resource '{name}' has an invalid mode configured - "
                f"valid: '{validate('DEFAULT_RESOURCE_MODE')}'!"
            )
            return False

        else:
            mode_supported, mode_fallback = supported_mode(m=res['mode'], t='resource', p=plugin)

            if not mode_supported:
                if mode_fallback is not None:
                    log(
                        f"Resource '{name}' has an unsupported mode configured - "
                        f"using fallback: '{mode_fallback}'.", lv=2
                    )

                else:
                    log(f"Resource '{name}' has an unsupported mode configured!")
                    return False

        return True

    def _check_monitoring(self, name: str, mon: dict, sys: bool = False) -> bool:
        if not value_exists(data=mon, key='plugin'):
            log(f"Monitoring '{name}' has no plugin configured!")
            return False

        if mon['plugin'] not in self.PLUGINS['monitoring']:
            log(
                f"Monitoring '{name}' has an non-existent plugin - "
                f"not found in: '{HARDCODED['PATH_PLUGIN']}/monitoring'!"
            )
            return False

        plugin = mon['plugin']
        if not value_exists(data=mon, key='plugin_args'):
            if max_plugin_args(t='monitoring', p=plugin) != 0:
                log(f"Monitoring '{name}' has no plugin-arguments configured!")
                return False

            log(f"Monitoring '{name}' has no plugin-arguments configured!", lv=3)

        else:
            if not enough_args(args=mon['plugin_args'], t='monitoring', p=plugin):
                log(f"Monitoring '{name}' has too few plugin-arguments configured!")
                return False

        if not value_exists(data=mon, key='interval'):
            log(
                f"Monitoring '{name}' has no interval configured - "
                f"using default: '{self.CONFIG_ENGINE['DEFAULT_MONITORING_WAIT']}'!",
                lv=3
            )

        if not sys and not value_exists(data=mon, key='vital'):
            log(
                f"Monitoring '{name}' has no vitality configured - "
                f"using default: '{self.CONFIG_ENGINE['DEFAULT_MONITORING_VITAL']}'!",
                lv=3
            )

        return True

    def _check_peer(self, name: str, peer: dict) -> bool:
        if not value_exists(data=peer, key='host'):
            log(f"Peer '{name}' has no host configured!")
            return False

        else:
            if not valid_host(peer['host']):
                log(f"Peer '{name}' seems to be neither valid IP nor (resolvable) DNS!")
                return False

        if not value_exists(data=peer, key='port'):
            log(
                f"Peer '{name}' has no port configured - "
                f"using default: '{self.CONFIG_ENGINE['DEFAULT_PEER_API_PORT']}'!",
                lv=3
            )

        elif not validate(item='DEFAULT_PEER_API_PORT', data=peer['port']):
            log(f"Peer '{name}' has an invalid port configured - valid: {validate(item='DEFAULT_PEER_API_PORT')}!")
            return False

        return True
