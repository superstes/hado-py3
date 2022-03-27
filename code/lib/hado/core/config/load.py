# checking config for errors, applying inheritance, converting to objects

from hado.util.debug import log
from hado.core.config.validate import validate
from hado.core.config.defaults import HARDCODED
from hado.core.app import App
from hado.util.helper import value_exists


class DeserializeConfig:
    def __init__(self, config_ha: dict, config_engine: dict):
        # note: not using global vars as this makes testing easier
        self.CONFIG_HA = config_ha
        self.CONFIG_ENGINE = config_engine
        self.LOADED = {'app': [], 'system': None, 'peer': []}

    def get(self) -> dict:
        if not self._check_engine():
            log('Got invalid engine config - exiting!')
            raise ValueError

        if not self._check_ha():
            log('Got invalid HA config - exiting!')
            raise ValueError

        glob_peers = self.CONFIG_HA['peers'] if 'peers' in self.CONFIG_HA else {}

        for name, app in self.CONFIG_HA['apps'].items():
            # use global peers if no app-specific ones are defined
            app['peers'] = glob_peers | app['peers'] if 'peers' in app else {}

            if self._check_app(name=name, app=app):
                self.LOADED['app'].append(App(name=name, app=app))

        if not value_exists(data=self.LOADED, key='app'):
            log('No app could be loaded - exiting!')
            raise ValueError

        return self.LOADED

    def _check_ha(self) -> bool:
        if not value_exists(data=self.CONFIG_HA, key='apps'):
            log("No 'apps' config found - exiting!")
            return False

        if not value_exists(data=self.CONFIG_HA, key='system'):
            log("No 'system' config found - using defaults and skipping system health monitoring!", 'WARNING')

        elif not value_exists(data=self.CONFIG_HA['system'], key='monitoring'):
            log("No 'system.monitoring' config found - skipping system health monitoring!", 'WARNING')

        return True

    def _check_engine(self) -> bool:
        ok = True

        for s, v in self.CONFIG_ENGINE.items():
            if not validate(item=s, data=v):
                log(f"Engine has an invalid '{s}' configured - valid: '{validate(s)}'!")
                ok = False

        return ok

    def _check_app(self, name: str, app: dict) -> bool:
        log(f"Checking config for app '{name}'.", 'INFO')

        if not value_exists(data=app, key='peers'):
            log(f"App '{name}' has no peers configured!")
            return False

        if not value_exists(data=app, key='resources'):
            log(f"App '{name}' has no resources configured!")
            return False

        if not value_exists(data=app, key='monitoring'):
            log(f"App '{name}' has no app-specific monitoring configured.", 'INFO')

        resources_ok = True
        monitoring_ok = True
        peers_ok = True

        for n, r in app['resources'].items():
            if not self._check_resource(name=n, res=r):
                resources_ok = False

        for n, p in app['peers'].items():
            if not self._check_peer(name=n, peer=p):
                peers_ok = False

        if value_exists(data=app, key='monitoring'):
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

        return True

    def _check_resource(self, name: str, res: dict) -> bool:
        if not value_exists(data=res, key='plugin'):
            log(f"Resource '{name}' has no plugin configured!")
            return False

        if not value_exists(data=res, key='plugin_args'):
            log(f"Resource '{name}' has no plugin-arguments configured!", 'WARNING')

        if not value_exists(data=res, key='vital'):
            log(f"Resource '{name}' has no vitality configured - using default: '{self.CONFIG_ENGINE['DEFAULT_RESOURCE_VITAL']}'!", 'INFO')

        if not value_exists(data=res, key='mode'):
            log(f"Resource '{name}' has no cluster-mode configured - using default: '{self.CONFIG_ENGINE['DEFAULT_RESOURCE_MODE']}'!", 'DEBUG')

        else:
            # mode alias-translation and validation
            m = res['mode']
            if m in HARDCODED['MODE']['ALIAS']:
                res['mode'] = HARDCODED['MODE']['ALIAS'][m]

            if not validate(item='DEFAULT_RESOURCE_MODE', data=res['mode']):
                log(f"Resource '{name}' has an invalid mode configured - valid: '{validate('DEFAULT_RESOURCE_MODE')}'!")
                return False

        return True

    def _check_monitoring(self, name: str, mon: dict) -> bool:
        if not value_exists(data=mon, key='plugin'):
            log(f"Monitoring '{name}' has no plugin configured!")
            return False

        if not value_exists(data=mon, key='plugin_args'):
            log(f"Monitoring '{name}' has no plugin-arguments configured!", 'WARNING')

        if not value_exists(data=mon, key='interval'):
            log(f"Monitoring '{name}' has no interval configured - using default: '{self.CONFIG_ENGINE['DEFAULT_MONITORING_INTERVAL']}'!", 'INFO')

    def _check_peer(self, name: str, peer: dict) -> bool:
        if not value_exists(data=peer, key='host'):
            log(f"Peer '{name}' has no host configured!")
            return False

        if not value_exists(data=peer, key='port'):
            log(f"Peer '{name}' has no port configured - using default: '{self.CONFIG_ENGINE['DEFAULT_SYNC_PORT']}'!", 'INFO')

        elif not validate(item='DEFAULT_SYNC_PORT', data=peer['port']):
            log(f"Peer '{name}' has an invalid port configured - valid: {validate(item='DEFAULT_SYNC_PORT')}!")
            return False

        return True
