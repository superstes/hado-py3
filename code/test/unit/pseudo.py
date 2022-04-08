from time import sleep
import warnings
from multiprocessing import Process
from waitress import serve
from flask import Flask

from hado.core.config.defaults import ENGINE as ENGINE_DEFAULTS
from hado.core.system import System

WAIT = 0.2


class PseudoPlugin:
    ACTIONS = {
        'check': 'WHIIII_CHECK',
    }

    def __init__(self, name: str, config: dict):
        self.name = name
        self.status = True
        self.vital = config['vital'] if 'vital' in config else True

    def action(self, a: str):
        try:
            print(f"{self.name}_{self.ACTIONS[a]}")

        except KeyError:
            pass

    def get_status(self) -> bool:
        return self.status


class PseudoMonitoring(PseudoPlugin):
    def __init__(self, name: str, config: dict, interval: int):
        super().__init__(name=name, config=config)
        self.interval = interval

    @property
    def stats(self) -> dict:
        return {self.name: self.status}


class PseudoResource(PseudoPlugin):
    ACTIONS = {
        'start': 'WHUPII_START',
        'stop': 'WHUPSII_STOP',
        'init': 'WHUPAA_INIT',
        'demote': 'WHUPO_DEMOTE',
        'promote': 'WHUPNN_PROMOTE',
        'fix': 'WHAAA_FIX',
    }

    def __init__(self, name: str, config: dict, sequence: int):
        super().__init__(name=name, config=config)
        self.sequence = sequence
        self.on_failure = config['on_failure'] if 'on_failure' in config else None
        self.on_shutdown = config['on_shutdown'] if 'on_shutdown' in config else None
        self.mode = config['mode'] if 'mode' in config else 'active-standby'

    @property
    def stats(self) -> dict:
        return {self.name: self.stats_raw}

    @property
    def stats_raw(self) -> dict:
        return {'up': True, 'active': self.status}


class PseudoAPI:
    def __init__(self):
        self.srv = Process(target=self._serve, name="Test Rest Server")

    def start(self):
        self.srv.start()
        sleep(WAIT)

    @staticmethod
    def _serve():
        from hado.api.get import api_get
        from hado.api.post import api_post
        api = Flask('HA-DO-TESTAPI')
        api.register_blueprint(api_get)
        api.register_blueprint(api_post)

        with warnings.catch_warnings():
            warnings.simplefilter('ignore')
            serve(
                app=api.wsgi_app,
                host=ENGINE_DEFAULTS['API_LISTEN_IP'],
                port=ENGINE_DEFAULTS['DEFAULT_PEER_API_PORT'],
            )

    def stop(self):
        self.srv.kill()
        self.srv.join()
        self.srv.close()
        sleep(WAIT)


class PseudoApp:
    # pylint: disable=R0902
    name = 'TEST'
    status = True
    health = 69
    resource_health = 69
    monitoring_health = 69
    peers = []

    def __init__(self, r: list, m: list):
        self.resources = r
        self.monitoring = m
        self.stats = {
            'status': self.status,
            'health': self.health,
            'health_res': self.resource_health,
            'health_mon': self.monitoring_health,
            'resources': {r.name: r.status for r in self.resources},
            'monitoring': {m.name: m.status for m in self.monitoring},
        }


class PseudoConfig:
    TEST_PLUGIN_R = PseudoResource(
        name='TestRes', config={}, sequence=1,
    )
    TEST_PLUGIN_M = PseudoMonitoring(
        name='TestAppMon', config={}, interval=1
    )
    TEST_SYSTEM = System(monitoring=[
        PseudoMonitoring(
            name='TestSystemMon', config={}, interval=1
        )
    ])

    CONFIG_LOADED = {
        'apps': [
            PseudoApp(
                r=[TEST_PLUGIN_R],
                m=[TEST_PLUGIN_M]
            )
        ],
        'system': TEST_SYSTEM,
        'peers': [],
    }
    CONFIG_ENGINE = ENGINE_DEFAULTS
