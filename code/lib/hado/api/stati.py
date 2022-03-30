from hado.core.app import App
from hado.core.plugin.resource import Resource
from hado.core.plugin.monitoring import Monitoring


def app_status(a: App) -> dict:
    return {
        'status': a.status,
        'health': a.health,
        'health_res': a.resource_health,
        'health_mon': a.monitoring_health,
        'resources': {r.name: r.status for r in a.resources}
    }


def plugin_status(p: (Resource, Monitoring)) -> dict:
    return {p.name: p.status}


def system_status() -> dict:
    return {}
