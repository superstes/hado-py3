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

import signal
from traceback import format_exc
from pathlib import Path
from time import time
from time import sleep as time_sleep
from sys import exc_info as sys_exc_info
from yaml import safe_load as yaml_load

from hado.util.threader import Loop as Thread
from hado.util.debug import log
from hado.api.server import RestServer
from hado.core.config.defaults import HARDCODED
from hado.core.config.dump import dump_defaults


class Service:
    def __init__(self):
        signal.signal(signal.SIGUSR1, self.stop)
        signal.signal(signal.SIGTERM, self.stop)
        signal.signal(signal.SIGINT, self.stop)
        self.CONFIG_HA = {}
        self.CONFIG_ENGINE = {}
        self.CONFIG_LOADED = {}
        self._init_config()
        self.THREADER = Thread()

    def start(self):
        try:
            self._thread(i=1, desc='HA-DO Rest-Server', d={'run': RestServer(), 'method': 'start'})

            self.THREADER.start()
            log('Start - finished starting threads.', lv=3)
            self._status()

        except TypeError as error_msg:
            log(f"Service encountered an error while starting:\n\"{error_msg}\"")
            self.stop()

        self._run()

    @staticmethod
    def stop(signum=None, stack=None):
        log(f"Service received signal {signum}", lv=2)
        raise SystemExit('Service exited.')

    def _init_config(self):
        # pylint: disable=W0611,C0415
        dump_defaults()

        if Path(HARDCODED['CONFIG_HA']).is_file():
            with open(HARDCODED['CONFIG_HA'], 'r') as cnf:
                self.CONFIG_HA = yaml_load(cnf.read())

            from hado.core.config.shared import init
            init()
            from hado.core.config.shared import CONFIG_HA, CONFIG_ENGINE, CONFIG_LOADED
            CONFIG_HA = self.CONFIG_HA
            CONFIG_ENGINE = self.CONFIG_ENGINE
            CONFIG_LOADED = self.CONFIG_LOADED

            if Path(HARDCODED['CONFIG_ENGINE']).is_file():
                with open(HARDCODED['CONFIG_HA'], 'r') as cnf:
                    self.CONFIG_ENGINE.update(yaml_load(cnf.read()))

            else:
                log(f"No custom engine config loaded (file: '{HARDCODED['CONFIG_ENGINE']}')", lv=3)

        else:
            log(f"Unable to load config from file: '{HARDCODED['CONFIG_HA']}'")
            self.stop()

    def _thread(self, i: int, d: dict, desc: str):
        # pylint: disable=W0612
        @self.THREADER.add_thread(
            sleep_time=i,
            thread_data=d,
            description=desc,
        )
        def thread_task(data: dict):
            getattr(data['run'], data['method'])()

    @staticmethod
    def _wait(seconds: int):
        start_time = time()

        while time() < start_time + seconds:
            time_sleep(1)

    def _status(self):
        thread_list = self.THREADER.list()
        simple_thread_list = [thread.name for thread in thread_list]
        log(f"Status - threads running: {simple_thread_list}", lv=3)
        if HARDCODED['DEBUG']:
            detailed_thread_list = '\n'.join([str(thread.__dict__) for thread in thread_list])
            log(f"Detailed info on running threads:\n{detailed_thread_list}", lv=4)

    def _run(self):
        # pylint: disable=W0702
        try:
            log('Entering service runtime')
            run_last_status_time = time()

            while True:
                if time() > (run_last_status_time + HARDCODED['SVC_INTERVAL_STATUS']):
                    self._status()
                    run_last_status_time = time()

                time_sleep(HARDCODED['SVC_INTERVAL_LOOP'])

        except:
            try:
                exc_type, error, _ = sys_exc_info()

                if str(error).find('Service exited') == -1:
                    log(f"A fatal error occurred: \"{exc_type} - {error}\"")
                    log(f"{format_exc(limit=HARDCODED['TRACEBACK_LINES'])}")

            except IndexError:
                pass

            self.stop()


Service().start()
