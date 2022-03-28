from hado.core.config.shared import CONFIG_ENGINE
from hado.core.plugin.driver import Plugin, PluginType, BasePluginUse


class Monitoring(BasePluginUse):
    plugin_type = PluginType.monitoring
    interval = CONFIG_ENGINE['DEFAULT_MONITORING_INTERVAL']

    def __init__(self, plugin_name: str, config: dict):
        super().__init__(
            vital=config['vital'] if 'vital' in config else CONFIG_ENGINE['DEFAULT_MONITORING_VITAL'],
            plugin=Plugin(
                plugin_type=self.plugin_type,
                name=plugin_name,
                args=config['plugin_args'] if 'plugin_args' in config else '',
            )
        )
        self._set_attr(data=config, attr='interval')

    def check(self) -> bool:
        return self.plugin.check()
