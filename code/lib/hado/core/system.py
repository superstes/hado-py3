from hado.core.config import shared


class System:
    # NOTE: system health/status will fallback to OK if no monitoring is defined

    def __init__(self, monitoring: []):
        self.monitoring = monitoring

    @property
    def health(self) -> float:
        h = [app.health for app in shared.CONFIG_LOADED['apps']]
        h.append(self.system_health)
        return sum(h) / len(h)

    @property
    def status(self) -> bool:
        s = [app.status for app in shared.CONFIG_LOADED['apps']]
        s.append(self.system_status)
        return all(s)

    @property
    def system_health(self) -> float:
        if len(self.monitoring) > 0:
            s = [m.status for m in self.monitoring]
            return (100 / len(s)) * s.count(True)

        return 100

    @property
    def system_status(self) -> bool:
        if len(self.monitoring) > 0:
            return all([m.status for m in self.monitoring])

        return True

    @property
    def stats(self) -> dict:
        # pylint: disable=R0801
        return {
            'status': self.status,
            'health': self.health,
            'health_system': self.system_health,
            'status_system': self.system_status,
        }
