from ..util.debug import log
from ..core.config import CONFIG_ENGINE, HARDCODED
from .plugin import Plugin, PluginType, BasePluginUse


class Monitoring(BasePluginUse):
    plugin_type = PluginType.monitoring

    def __init__(self, plugin_name: str, config: dict):
        super().__init__(
            vital=config['vital'] if 'vital' in config else CONFIG_ENGINE['DEFAULT_MONITORING_VITAL'],
            plugin=Plugin(
                plugin_type=self.plugin_type,
                base=f"{HARDCODED['PATH_PLUGIN']}/monitoring",
                name=plugin_name,
                args=config['plugin_args'] if 'plugin_args' in config else '',
            )
        )
        self.interval = config['interval'] if 'interval' in config else CONFIG_ENGINE['DEFAULT_MONITORING_INTERVAL']

    def check(self):
        return self.plugin.check()
