from ..util.debug import log
from ..core.config import CONFIG_ENGINE, HARDCODED
from .plugin import Plugin, PluginType, BasePluginUse


class Resource(BasePluginUse):
    plugin_type = PluginType.resource

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
        self.on_failure = config['on_failure'] if 'on_failure' in config else None
        self.on_shutdown = config['on_shutdown'] if 'on_shutdown' in config else None
        self.mode = config['mode'] if 'mode' in config else CONFIG_ENGINE['DEFAULT_RESOURCE_MODE']
        self.mode_prio = config['mode_prio'] if 'mode_prio' in config else CONFIG_ENGINE['DEFAULT_RESOURCE_MODE_PRIO']

    def action(self, do: str) -> bool:
        if do in self.plugin.CMDS:
            getattr(self.plugin, do)()
            return True

        return False
