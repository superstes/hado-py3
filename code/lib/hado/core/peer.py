# peer stati and sync-pull
from json import JSONDecodeError
from datetime import datetime
from requests import exceptions
from requests import get as get_url
from requests.auth import HTTPBasicAuth

from hado.util.helper import tcp_ping
from hado.core.config import shared
from hado.core.config.defaults import HARDCODED
from hado.util.debug import log
from hado.api.util import HTTP_STATI

# pylint: disable=R0913


class Peer:
    UP_CHECK_TIMEOUT = 0.5

    def __init__(self, name: str, host: str, port: int,
                 auth: bool, user: str, pwd: str):
        self.name = name
        self.auth = auth
        self.user = user
        self.pwd = pwd
        self.host = host
        self.port = port
        proto = 'https' if shared.CONFIG_ENGINE['API_SYNC_SSL'] else 'http'
        self.url = f"{proto}://{self.host}:{self.port}/{HARDCODED['API_SYNC_PATH']}"
        self.log_id = f"Peer - {self.name} - {self.host}:{self.port} -"
        self.up = None
        self.last_sync = None
        self.last_change = None
        self.last_data = None
        self.last_seen = None
        self.data_history = {}

    def fetch(self):
        if self.is_up:
            data = self._request()
            if data is not None and len(data) > 0:
                self._update(data=data)

    def _request(self) -> dict:
        data = {}
        params = {
            'url': self.url,
            'headers': {'user-agent': HARDCODED['API_SYNC_UA']},
            'timeout': shared.CONFIG_ENGINE['API_SYNC_TIMEOUT'],
        }

        if self.auth:
            params['auth'] = HTTPBasicAuth(self.user, self.pwd)

        if shared.CONFIG_ENGINE['API_SYNC_SSL'] and \
                not shared.CONFIG_ENGINE['API_SYNC_SSL_VERIFY']:
            params['verify'] = False

        try:
            r = get_url(**params)

            try:
                data = r.json()

            except JSONDecodeError:
                data = None

            if r.status_code != HTTP_STATI['OK']:
                log(
                    f"{self.log_id} Sync failed! "
                    f"Remote server returned error: '{data}'"
                )

        except exceptions.RequestException:
            log(
                f"{self.log_id} Sync failed! "
                f"Remote server is unreachable!"
            )

        return data

    def _update(self, data: dict) -> bool:
        time = datetime.now()
        r = False
        self.last_sync = time

        if self.last_data != data:
            self.data_history[time] = data
            self.last_data = data
            self.last_change = time
            r = True

        if len(self.data_history) > shared.CONFIG_ENGINE['PEER_HISTORY_MAX']:
            self.data_history.pop(min(self.data_history))

        return r

    @property
    def is_up(self) -> bool:
        _u = tcp_ping(host=self.host, port=self.port, timeout=self.UP_CHECK_TIMEOUT)
        self.up = _u

        if _u:
            self.last_seen = datetime.now()

        return _u

    def start(self):
        pass

    @property
    def apps(self) -> list:
        return [a for a in shared.CONFIG_LOADED['apps'] if self in a.peers]

    @property
    def stats(self) -> dict:
        return {self.name: self.stats_raw}

    @property
    def stats_raw(self) -> dict:
        return {
            'up': self.up,
            'last_seen': f"{self.last_seen}",
            'last_sync': f"{self.last_sync}",
            'last_change': f"{self.last_change}",
            'sync': {
                'url': self.url,
                'user': self.user,
            },
            'apps': [a.name for a in self.apps]
        }

    def __repr__(self):
        return f"HA-DO PEER: {self.__dict__}".replace(self.pwd, '********')
