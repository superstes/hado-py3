from hado.util.debug import log
from hado.core.config.shared import CONFIG_ENGINE
from hado.core.resource import Resource
from hado.core.monitoring import Monitoring


class App:
    REACTIONS = ['stop', 'demote', 'leave']
    on_failure = CONFIG_ENGINE['DEFAULT_ACTION_FAILURE']
    on_shutdown = CONFIG_ENGINE['DEFAULT_ACTION_SHUTDOWN']

    def __init__(self, name: str, app: dict):
        self.name = name
        self.log_id = f"App - {self.name} -"

        self.resources = []
        next_seq = self._get_highest_sequence(app['resources']) + 1
        for name, res in app['resources'].items():
            self.resources.append(Resource(
                plugin_name=name,
                config=res,
                sequence=res['sequence'] if 'sequence' in res else next_seq,
            ))
            if 'sequence' not in res:
                next_seq += 1

        self.monitoring = []
        if 'monitoring' in app:
            for name, mon in app['monitoring'].items():
                self.monitoring.append(Monitoring(
                    plugin_name=name,
                    config=mon,
                ))

        self._set_attr(data=app, attr='on_failure')
        self._set_attr(data=app, attr='on_shutdown')

        self.action('init')

    def check(self):
        log(f"{self.log_id} Starting check!", 'DEBUG')

        # failover handling should be abstracted into separate class
        # check handling should also be separated

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
        log(f"{self.log_id} Starting failure actions!")
        if self.on_failure in self.REACTIONS:
            a = self.on_failure
            for r in self.resources:
                if r.on_failure is not None:
                    a = r.on_failure

                if a != 'leave':
                    r.action(a)

    def shutdown(self):
        log(f"{self.log_id} Starting shutdown actions!")
        if self.on_shutdown in self.REACTIONS:
            a = self.on_shutdown
            for r in self.resources:
                if r.on_shutdown is not None:
                    a = r.on_shutdown

                if a != 'leave':
                    r.action(a)

    def action(self, do: str):
        for r in self.resources:
            r.action(do)

    @property
    def resource_health(self) -> float:
        s = [r.status for r in self.resources]
        return (100 / len(s)) * s.count(True)

    @property
    def monitoring_health(self) -> float:
        s = [m.status for m in self.monitoring]
        return (100 / len(s)) * s.count(True)

    @property
    def health(self) -> float:
        s = [r.status for r in self.resources]
        s.extend([m.status for m in self.monitoring])
        return (100 / len(s)) * s.count(True)

    @property
    def running(self) -> bool:
        s = [r.status for r in self.resources if r.vital]
        s.extend([m.status for m in self.resources if m.vital])
        return all(s)

    @property
    def failed(self) -> bool:
        return not self.running

    @property
    def status(self) -> int:
        return 1 if self.running else 0

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
