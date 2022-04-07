#!/usr/bin/python3.9
# This file is part of HA-DO
#     Copyright (C) 2022 Superstes
#
#     GrowAutomation is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
#
#     This program is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.
#
#     You should have received a copy of the GNU General Public License
#     along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
#     E-Mail: contact@superstes.eu
#     Web: https://hado.superstes.eu


# environmental variable PYTHONPATH must be set to the HA-DO root-path for imports to work
#   (export PYTHONPATH=/var/lib/hado)
#   it's being set automatically by the systemd service

# pylint: disable=C0415,W0702,W0703

import signal
from traceback import format_exc
from pathlib import Path
from time import time
from time import sleep as time_sleep
from sys import exc_info as sys_exc_info
from yaml import safe_load as yaml_load

from hado.util.debug import log
from hado.core.config.defaults import HARDCODED, ENGINE
from hado.core.config.dump import dump_defaults
from hado.core.config import shared
from hado.util.threader import Loop as Thread


class Service:
    def __init__(self):
        signal.signal(signal.SIGUSR1, self.stop)
        signal.signal(signal.SIGTERM, self.stop)
        signal.signal(signal.SIGINT, self.stop)
        self.CONFIG_HA = {}
        self.CONFIG_ENGINE = ENGINE
        self.THREADER = Thread()

    def start(self):
        try:
            # import only possible after config-initialization
            from hado.api import server
            from hado.core.switch.fetch import add_workers

            self._thread(i=1, desc='HA-DO Rest-Server', d={'run': server, 'method': 'start'})
            add_workers(threader=self.THREADER)

            self.THREADER.start()
            log('Start - finished starting threads.', lv=3)
            self._status()

        except Exception as e:
            log(f"Service encountered an error while starting: \"{e}\"")
            log(format_exc(limit=shared.CONFIG_ENGINE['TRACEBACK_LINES']))
            self.stop()

        self._run()

    @staticmethod
    def stop(signum=None, stack=None):
        if signum is not None:
            log(f"Service received signal {signum}", lv=2)

        raise SystemExit('Service exited.')

    def init_config(self) -> bool:
        dump_defaults()

        config_ha = f"{HARDCODED['PATH_CONFIG']}/{HARDCODED['FILE_CONFIG_HA']}"
        config_engine = f"{HARDCODED['PATH_CONFIG']}/{HARDCODED['FILE_CONFIG_ENGINE']}"

        if Path(config_ha).is_file():
            with open(config_ha, 'r') as cnf:
                self.CONFIG_HA = yaml_load(cnf.read())

            shared.init()
            shared.CONFIG_HA = self.CONFIG_HA
            shared.CONFIG_ENGINE = self.CONFIG_ENGINE

            engine_ok = False
            if Path(config_engine).is_file():
                try:
                    with open(config_engine, 'r') as cnf:
                        self.CONFIG_ENGINE.update(yaml_load(cnf.read()))
                        engine_ok = True

                except TypeError:
                    pass

            if not engine_ok:
                log(f"No custom engine config loaded (file: '{config_engine}')", lv=3)

        else:
            log(f"Unable to load config from file: '{config_ha}'")
            self.stop()
            return False

        from hado.core.config.load import DeserializeConfig
        shared.CONFIG_LOADED = DeserializeConfig(
            config_ha=self.CONFIG_HA,
            config_engine=self.CONFIG_ENGINE,
        ).get()
        return True

    def _thread(self, i: int, d: dict, desc: str):
        # pylint: disable=W0612
        @self.THREADER.add_thread_deco(
            sleep=i,
            thread_data=d,
            description=desc,
        )
        def thread_task(data: dict):
            getattr(data['run'], data['method'])()

    def _status(self):
        log(
            f"Status - threads running: "
            f"{[thread.description for thread in self.THREADER.list()]}",
            lv=3
        )
        if self.CONFIG_ENGINE['DEBUG']:
            detailed_thread_list = '\n'.join([str(thread.__dict__) for thread in self.THREADER.list()])
            log(f"Detailed info on running threads:\n{detailed_thread_list}", lv=4)

    def _run(self):
        try:
            log('Entering service runtime', lv=3)
            run_last_status_time = time()

            while True:
                if time() > (run_last_status_time + self.CONFIG_ENGINE['SVC_INTERVAL_STATUS']):
                    self._status()
                    run_last_status_time = time()

                time_sleep(self.CONFIG_ENGINE['SVC_INTERVAL_LOOP'])

        except:
            try:
                exc_type, error, _ = sys_exc_info()

                if str(error).find('Service exited') == -1:
                    log(f"A fatal error occurred: \"{exc_type} - {error}\"")
                    log(format_exc(limit=self.CONFIG_ENGINE['TRACEBACK_LINES']))

            except IndexError:
                pass

            self.stop()


if __name__ == '__main__':
    # init-process split for testing
    svc = Service()
    svc.init_config()
    svc.start()
