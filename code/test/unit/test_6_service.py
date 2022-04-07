# Test functionality of the service-object

from os import getcwd, remove
# from time import time, sleep
from pathlib import Path
from re import match as regex_match
import pytest

from hado.service.run import Service

from .util import capsys_error

WAIT = 0.2


class TestService:
    def test_service_start_status(self, mocker):
        mocker.patch('hado.service.run.Service._thread', return_value=None)
        mocker.patch('hado.core.switch.fetch.add_workers', return_value=None)

    def test_service_stop(self, capsys, mocker):
        mocker.patch('hado.util.threader.log', return_value=None)

        with pytest.raises(SystemExit):
            Service().stop()

        capsys.readouterr()
        with pytest.raises(SystemExit):
            Service().stop(signum=69)
            stdout, _ = capsys.readouterr()
            assert regex_match(".*received signal.*", stdout.replace('\n', ' '))

    # def test_service_thread(self):
    #     test_file = '/tmp/aaaaaaaa'
    #     desc = 'TestThread_1'
    #     svc = Service()
    #
    #     class TestProc:
    #         @staticmethod
    #         def start():
    #             with open(test_file, 'w+') as f:
    #                 f.write('test')
    #
    #     svc._thread(
    #         i=5,
    #         d={'run': TestProc(), 'method': 'start'},
    #         desc=desc,
    #     )
    #     svc.THREADER.start()
    #     sleep(WAIT)
    #     svc.THREADER.stop()
    #     sleep(WAIT)
    #     assert Path(test_file).is_file()
    #     remove(test_file)

    def test_service_init_config(self, capsys, mocker):
        mocker.patch('hado.util.threader.log', return_value=None)

        class PseudoDesi:
            @staticmethod
            def get():
                pass

        from hado.core.config.defaults import HARDCODED
        h = HARDCODED.copy()
        h['PATH_CONFIG'] = f"{getcwd()}/../etc"
        h['PATH_PLUGIN'] = f"{getcwd()}/../test/data/plugin"
        mocker.patch('hado.service.run.HARDCODED', h)
        mocker.patch('hado.core.config.dump.HARDCODED', h)
        mocker.patch('hado.core.config.load.DeserializeConfig', side_affect=PseudoDesi)
        mocker.patch('hado.service.run.Service.stop', return_value=None)
        dump_file = f"{h['PATH_CONFIG']}/{h['FILE_CONFIG_ENGINE_DEFAULTS']}"

        svc = Service()

        assert svc.init_config()
        assert Path(dump_file).is_file()
        remove(dump_file)
        capsys.readouterr()

        h['FILE_CONFIG_HA'] = 'doesNotExist.yml'
        assert not svc.init_config()
        stdout, _ = capsys.readouterr()
        capsys_error(stdout)
        assert Path(dump_file).is_file()
        remove(dump_file)
