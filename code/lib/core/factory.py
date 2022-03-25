from ..util.debug import log
from ..core.config import CONFIG_ENGINE


class System:
    def __init__(self):
        pass

    def get(self):
        pass


class SerializeConfig:
    def __init__(self, config: dict):
        self.CONFIG = config

    def get(self):
        self._check()
        for name, app in self.CONFIG['apps'].items():
            if self._check_app(name=name, app=app):
                # todo: build object-based config
                pass

    def _check(self):
        if 'apps' not in self.CONFIG or len(self.CONFIG['apps']) == 0:
            log("No 'apps' config found - nothing to do!")
            raise SystemExit

        if 'system' not in self.CONFIG:
            log("No 'system' config found - using defaults and skipping system health monitoring!", 'WARNING')

        elif 'monitoring' not in self.CONFIG['system']:
            log("No 'system.monitoring' config found - skipping system health monitoring!", 'WARNING')

    @staticmethod
    def _check_app(name: str, app: dict) -> bool:
        if 'resources' not in app or len(app['resources']) == 0:
            log(f"No resources configured for app '{name}'!")
            return False

        if 'monitoring' not in app or len(app['monitoring']) == 0:
            log(f"No monitoring configured for app '{name}'", 'INFO')

        return True

    @staticmethod
    def _check_resource(name: str, res: dict) -> bool:
        if 'plugin' not in res:
            log(f"No plugin configured for resource '{name}'!")
            return False

        if 'plugin_args' not in res:
            log(f"No plugin-arguments configured for resource '{name}'!", 'WARNING')

        if 'vital' not in res:
            log(f"Resource '{name}' vitality not declared - using default: '{CONFIG_ENGINE['DEFAULT_RESOURCE_VITAL']}'!", 'INFO')

        if 'mode' not in res:
            log(f"No cluster-mode configured for resource '{name}' - using default: '{CONFIG_ENGINE['DEFAULT_RESOURCE_MODE']}'!", 'DEBUG')

        return True

    @staticmethod
    def _check_monitoring(name: str, mon: dict) -> bool:
        if 'plugin' not in mon:
            log(f"No plugin configured for monitoring '{name}'!")
            return False

        if 'plugin_args' not in mon:
            log(f"No plugin-arguments configured for monitoring '{name}'!", 'WARNING')

        if 'interval' not in mon:
            log(f"No interval configured for monitoring '{name}' - using default: '{CONFIG_ENGINE['DEFAULT_MONITORING_INTERVAL']}'!", 'WARNING')
