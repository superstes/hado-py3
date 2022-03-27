from hado.util.debug import log
from hado.core.config.shared import CONFIG_ENGINE
from hado.core.config.defaults import HARDCODED
from hado.core.plugin import Plugin, PluginType, BasePluginUse


class Resource(BasePluginUse):
    plugin_type = PluginType.resource
    on_failure = None
    on_shutdown = None
    mode = CONFIG_ENGINE['DEFAULT_RESOURCE_MODE']
    mode_prio = CONFIG_ENGINE['DEFAULT_RESOURCE_MODE_PRIO']

    def __init__(self, plugin_name: str, config: dict, sequence: int):
        super().__init__(
            vital=config['vital'] if 'vital' in config else CONFIG_ENGINE['DEFAULT_RESOURCE_VITAL'],
            plugin=Plugin(
                plugin_type=self.plugin_type,
                base=f"{HARDCODED['PATH_PLUGIN']}/resource",
                name=plugin_name,
                args=config['plugin_args'],
            )
        )
        self.sequence = sequence
        self._set_attr(data=config, attr='on_failure')
        self._set_attr(data=config, attr='on_shutdown')
        self._set_attr(data=config, attr='mode')
        self._set_attr(data=config, attr='mode_prio')

    def action(self, do: str) -> bool:
        if do in self.plugin.CMDS:
            return getattr(self.plugin, do)()

        return False