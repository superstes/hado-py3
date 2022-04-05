from hado.core.config import shared
from hado.core.plugin.driver import Plugin, PluginType, BasePluginUse


class Monitoring(BasePluginUse):
    plugin_type = PluginType.monitoring
    interval = shared.CONFIG_ENGINE['DEFAULT_MONITORING_INTERVAL']

    def __init__(self, name: str, config: dict):
        if 'vital' in config:
            v = config['vital']
        else:
            v = shared.CONFIG_ENGINE['DEFAULT_MONITORING_VITAL']

        super().__init__(
            vital=v,
            plugin=Plugin(
                plugin_type=self.plugin_type,
                name=config['plugin'],
                args=config['plugin_args'] if 'plugin_args' in config else [],
            )
        )
        self.name = name
        self._set_attr(data=config, attr='interval')

    @property
    def status(self) -> bool:
        return self.plugin.check()

    def __repr__(self):
        return f"HA-DO MONITORING: {self.__dict__}"


class SystemMonitoring(BasePluginUse):
    plugin_type = PluginType.monitoring
    interval = shared.CONFIG_ENGINE['DEFAULT_MONITORING_INTERVAL']

    def __init__(self, name: str, config: dict):
        super().__init__(
            vital=True,  # system is always vital
            plugin=Plugin(
                plugin_type=self.plugin_type,
                name=config['plugin'],
                args=config['plugin_args'] if 'plugin_args' in config else [],
            )
        )
        self.name = name
        self._set_attr(data=config, attr='interval')

    @property
    def status(self) -> bool:
        return self.plugin.check()

    def __repr__(self):
        return f"HA-DO SYSTEM-MONITORING: {self.__dict__}"
