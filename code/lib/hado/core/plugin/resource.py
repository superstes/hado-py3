from hado.core.config import shared
from hado.core.plugin.driver import Plugin, PluginType, BasePluginUse


class Resource(BasePluginUse):
    plugin_type = PluginType.resource
    on_failure = None
    on_shutdown = None
    mode = shared.CONFIG_ENGINE['DEFAULT_RESOURCE_MODE']
    mode_prio = shared.CONFIG_ENGINE['DEFAULT_RESOURCE_MODE_PRIO']

    def __init__(self, name: str, config: dict, sequence: int):
        super().__init__(
            vital=config['vital'] if 'vital' in config else shared.CONFIG_ENGINE['DEFAULT_RESOURCE_VITAL'],
            plugin=Plugin(
                plugin_type=self.plugin_type,
                name=config['plugin'],
                args=config['plugin_args'] if 'plugin_args' in config else [],
            )
        )
        self.name = name
        self.sequence = sequence
        self.up = None
        self.other_active = None
        self.cluster_leader = None
        self._set_attr(data=config, attr='on_failure')
        self._set_attr(data=config, attr='on_shutdown')
        self._set_attr(data=config, attr='mode')
        self._set_attr(data=config, attr='mode_prio')

    def action(self, do: str) -> bool:
        if do in self.plugin.CMDS:
            return getattr(self.plugin, do)()

        return False

    def get_status(self) -> bool:
        _s = self.plugin.is_active
        self.status = _s
        return _s

    def get_up(self) -> bool:
        _o = self.plugin.is_other
        _u = any([self.other_active, self.status])
        self.other_active = _o
        self.up = _u
        return _u

    def get_leader(self) -> bool:
        _l = self.plugin.is_leader
        self.cluster_leader = _l
        return self.cluster_leader

    @property
    def stats(self) -> dict:
        return {self.name: self.stats_raw}

    @property
    def stats_raw(self) -> dict:
        return {'up': self.up, 'active': self.status}

    def __repr__(self):
        return f"HA-DO RESOURCE: {self.__dict__}"
