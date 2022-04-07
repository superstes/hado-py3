# creating threads for status-updates/-checks

from hado.core.peer import Peer
from hado.core.plugin.monitoring import Monitoring, SystemMonitoring
from hado.core.plugin.resource import Resource
from hado.util.threader import Loop
from hado.core.config import shared


def _fetch_resource_status(data: Resource):
    data.get_status()


def _fetch_resource_up(data: Resource):
    data.get_up()


def _fetch_resource_leader(data: Resource):
    data.get_leader()


def _fetch_monitoring(data: (Monitoring, SystemMonitoring)):
    data.get_status()


def _fetch_peer(data: Peer):
    data.fetch()


def add_workers(threader: Loop):
    for peer in shared.CONFIG_LOADED['peers']:
        if len(peer.apps) > 0:
            threader.add_thread(
                execute=_fetch_peer,
                sleep=shared.CONFIG_ENGINE['CHECK_WAIT'],
                thread_data=peer,
                description=f"Peer '{peer.name}' sync"
            )

    for mon in shared.CONFIG_LOADED['system'].monitoring:
        threader.add_thread(
            execute=_fetch_monitoring,
            sleep=mon.interval,
            thread_data=mon,
            description=f"System monitoring '{mon.name}'"
        )

    for app in shared.CONFIG_LOADED['apps']:
        for mon in app.monitoring:
            threader.add_thread(
                execute=_fetch_monitoring,
                sleep=mon.interval,
                thread_data=mon,
                description=f"App '{app.name}' monitoring '{mon.name}'"
            )

        for res in app.resources:
            threader.add_thread(
                execute=_fetch_resource_status,
                sleep=shared.CONFIG_ENGINE['CHECK_WAIT'],
                thread_data=res,
                description=f"App '{app.name}' resource '{res.name}' - status check"
            )

            if res.mode != 'standalone':
                threader.add_thread(
                    execute=_fetch_resource_up,
                    sleep=shared.CONFIG_ENGINE['CHECK_WAIT'],
                    thread_data=res,
                    description=f"App '{app.name}' resource '{res.name}' - up check"
                )

            if res.mode not in ['standalone', 'active-standby']:
                threader.add_thread(
                    execute=_fetch_resource_leader,
                    sleep=shared.CONFIG_ENGINE['CHECK_WAIT'],
                    thread_data=res,
                    description=f"App '{app.name}' resource '{res.name}' - leader check"
                )
