from hado.core.config.shared import CONFIG_ENGINE
from hado.core.plugin.driver import Plugin, PluginType, BasePluginUse


class Monitoring(BasePluginUse):
    plugin_type = PluginType.monitoring
    interval = CONFIG_ENGINE['DEFAULT_MONITORING_INTERVAL']

    def __init__(self, config: dict):
        if 'vital' in config:
            v = config['vital']
        else:
            v = CONFIG_ENGINE['DEFAULT_MONITORING_VITAL']

        super().__init__(
            vital=v,
            plugin=Plugin(
                plugin_type=self.plugin_type,
                name=config['plugin'],
                args=config['plugin_args'] if 'plugin_args' in config else '',
            )
        )
        self._set_attr(data=config, attr='interval')

    def check(self) -> bool:
        return self.plugin.check()

    def __repr__(self):
        return f"HA-DO MONITORING: {self.__dict__}"
