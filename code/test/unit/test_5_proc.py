# Test functions that run external processes

from time import time, sleep
from pathlib import Path
from os import remove
from re import match as regex_match

from hado.util.threader import Loop
from hado.util.process import subprocess

from .util import capsys_error

WAIT = 0.2


def thread(threader, d: dict, desc: str):
    # pylint: disable=W0612
    @threader.add_thread_deco(
        sleep=0.1,
        thread_data=d,
        description=desc,
        once=True,
    )
    def thread_task(data: dict):
        getattr(data['run'], data['method'])()


def process_error(c) -> bool:
    stdout, stderr = c.readouterr()
    return any([
        capsys_error(stdout),
        capsys_error(stderr)
    ])


class TestProcessing:
    def test_thread_start(self):
        test_file = f'/tmp/{time()}'
        desc = 'TestThread_1'

        class TestProc:
            @staticmethod
            def start():
                with open(test_file, 'w+') as f:
                    f.write('test')

        t = Loop()
        thread(
            threader=t,
            d={'run': TestProc(), 'method': 'start'},
            desc=desc,
        )
        t.start()

        sleep(WAIT)
        del t
        assert Path(test_file).is_file()
        remove(test_file)

    def test_thread_start_single(self):
        test_file = f'/tmp/{time()}'
        desc = 'TestThread_2'

        class TestProc:
            @staticmethod
            def start():
                with open(test_file, 'w+') as f:
                    f.write('test')

        t = Loop()
        thread(
            threader=t,
            d={'run': TestProc(), 'method': 'start'},
            desc=desc,
        )

        t.start_thread(description=desc)
        sleep(WAIT)
        del t
        assert Path(test_file).is_file()
        remove(test_file)

    def test_thread_stop(self):
        test_file = f'/tmp/{time()}'
        desc = 'TestThread_3'

        class TestProc:
            @staticmethod
            def start():
                with open(test_file, 'w+') as f:
                    f.write('test')

                sleep(WAIT)

            def __del__(self):
                remove(test_file)

        t = Loop()
        thread(
            threader=t,
            d={'run': TestProc(), 'method': 'start'},
            desc=desc,
        )
        t.start()

        sleep(WAIT)
        assert Path(test_file).is_file()
        t.stop()
        del t
        sleep(WAIT)
        assert not Path(test_file).is_file()

    def test_thread_list(self):
        desc = 'TestThread_4'

        class TestProc:
            @staticmethod
            def start():
                sleep(1)

        t = Loop()
        thread(
            threader=t,
            d={'run': TestProc(), 'method': 'start'},
            desc=desc,
        )
        t.start()
        tl = t.list()

        sleep(WAIT)
        del t
        assert isinstance(tl, set)
        assert len(tl) == 1
        tl_item = list(tl)[0]
        assert hasattr(tl_item, 'data')
        assert isinstance(tl_item.data, dict)

    def test_thread_reload(self):
        test_file = f'/tmp/{time()}'
        desc = 'TestThread_5'

        class TestProc:
            @staticmethod
            def start():
                with open(test_file, 'w+') as f:
                    f.write('test')

                sleep(1)

        t = Loop()
        thread(
            threader=t,
            d={'run': TestProc(), 'method': 'start'},
            desc=desc,
        )
        t.start()

        sleep(WAIT)
        assert Path(test_file).is_file()
        remove(test_file)
        assert not Path(test_file).is_file()
        assert t.reload_thread(description=desc)
        sleep(WAIT)
        assert Path(test_file).is_file()
        del t
        remove(test_file)

    def test_process_basic(self, capsys):
        test_file = f'/tmp/{time()}'
        subprocess(cmd=['touch', test_file])
        assert Path(test_file).is_file()
        assert not process_error(capsys)
        subprocess(cmd=['rm', test_file])
        assert not Path(test_file).is_file()
        assert not process_error(capsys)

    def test_process_stdout(self, capsys):
        test_file = f'/tmp/{time()}'
        test_string = 'fa9u3lowkw3h8rh'
        subprocess(cmd=f"echo '{test_string}' > {test_file}", shell=True)
        assert Path(test_file).is_file()
        assert not process_error(capsys)
        o = subprocess(cmd=['cat', test_file])
        assert o == test_string
        assert not process_error(capsys)
        remove(test_file)

    def test_process_failure(self, capsys):
        subprocess(cmd=['rm', '/tmp/doesNotExist.raaaaaandoooommm'])
        assert process_error(capsys)

    def test_process_shell(self, capsys):
        subprocess(cmd='touch /tmp/doesNotExist.raa')
        stdout, _ = capsys.readouterr()
        capsys_error(stdout)
        assert regex_match(f'.*was not formatted as expected.*', stdout.replace('\n', ' '))
