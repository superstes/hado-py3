from hado.util.debug import log
from hado.core.config.shared import CONFIG_ENGINE
from hado.core.plugin.resource import Resource
from hado.core.plugin.monitoring import Monitoring
from hado.core.plugin.driver import plugin_cmds, PluginType


class App:
    on_failure = CONFIG_ENGINE['DEFAULT_ACTION_FAILURE']
    on_shutdown = CONFIG_ENGINE['DEFAULT_ACTION_SHUTDOWN']

    def __init__(self, name: str, app: dict):
        self._app_config = app
        self.name = name
        self.log_id = f"App - {self.name} -"
        self.resources = []
        self.monitoring = []
        self._set_attr(data=app, attr='on_failure')
        self._set_attr(data=app, attr='on_shutdown')

    def init_resources(self):
        _init = False

        if len(self.resources) == 0:
            _init = True
            next_seq = self._get_highest_sequence(self._app_config['resources']) + 1
            for n, res in self._app_config['resources'].items():
                self.resources.append(Resource(
                    name=n,
                    config=res,
                    sequence=res['sequence'] if 'sequence' in res else next_seq,
                ))
                if 'sequence' not in res:
                    next_seq += 1

        if len(self.monitoring) == 0:
            _init = True
            if 'monitoring' in self._app_config:
                for n, mon in self._app_config['monitoring'].items():
                    self.monitoring.append(Monitoring(config=mon, name=n))

        if _init:
            self.action('init')

    def check(self):
        log(f"{self.log_id} Starting check!", lv=4)

        # failover handling should be abstracted into separate class
        # check handling should also be separated

        # basic ideas => should probably be formed in some kind of 'mode-switches'
        # if failed
        #   try to recover
        #     wait (min time..) and try to start failed resources
        #     run resource fix if available
        #   if unsuccessful
        #     fail whole app
        #     failure handling should be configured
        #       pe. wait for n seconds and retry (fail-sleep)
        #       pe. wait and run notification task (mail admin that it failed)

        # sync workflow
        #   list all peers that have configured this app on init
        #     config check of peers? check that they have the same resources configured
        #   loop over resources
        #     if not standalone
        #       check peers stati and modi
        #     if active-active
        #       if none is master => promote the active node with the lowest mode_prio (promote)
        #       if lower prio is also master => demote this node (demote)
        #     if active-passive
        #       if no other is active => make sure this node is (start)
        #       if this node is active => make sure no other is (stop)

    def failure(self):
        log(f"{self.log_id} Starting failure actions!", lv=2)
        a = self.on_failure
        for r in self.resources:
            if r.on_failure is not None:
                a = r.on_failure

            if a != 'leave':
                r.action(a)

    def shutdown(self):
        log(f"{self.log_id} Starting shutdown actions!", lv=2)
        a = self.on_shutdown
        for r in self.resources:
            if r.on_shutdown is not None:
                a = r.on_shutdown

            if a != 'leave':
                r.action(a)

    def action(self, do: str):
        if do in plugin_cmds[PluginType.resource]:
            for r in self.resources:
                r.action(do)

        elif do in plugin_cmds[PluginType.monitoring]:
            for m in self.monitoring:
                m.action(do)

        else:
            log(f"{self.log_id} Got unsupported action: '{do}' - ignoring!", lv=2)

    def _res_exists(self) -> bool:
        if len(self.resources) == 0:
            return False

        return True

    def _mon_exists(self) -> bool:
        if len(self.monitoring) == 0:
            return False

        return True

    @property
    def resource_health(self) -> float:
        if self._res_exists():
            s = [r.status for r in self.resources]
            return (100 / len(s)) * s.count(True)

        return 0.0

    @property
    def monitoring_health(self) -> float:
        if self._mon_exists():
            s = [m.status for m in self.monitoring]
            return (100 / len(s)) * s.count(True)

        return 0.0

    @property
    def health(self) -> float:
        if self._res_exists() and self._mon_exists():
            s = [r.status for r in self.resources]
            s.extend([m.status for m in self.monitoring])
            return (100 / len(s)) * s.count(True)

        return 0.0

    @property
    def status(self) -> bool:
        if self._res_exists() and self._mon_exists():
            s = [r.status for r in self.resources if r.vital]
            s.extend([m.status for m in self.monitoring if m.vital])
            return all(s)

        return False

    @property
    def failed(self) -> bool:
        return not self.status

    def _set_attr(self, data: dict, attr: str):
        if attr in data:
            setattr(self, attr, data[attr])

    @staticmethod
    def _get_highest_sequence(resources: dict) -> int:
        seqs = [0]

        for res in resources:
            if 'sequence' in res:
                seqs.append(int(res['sequence']))

        return max(seqs)

    def __repr__(self):
        return f"HA-DO APP: {self.__dict__}"
