# Test functions that run external processes

from time import time, sleep
from pathlib import Path
from os import remove
from re import match as regex_match

from hado.util.threader import Loop
from hado.util.process import subprocess


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
        regex_match('.*ERROR.*', stdout.replace('\n', ' ')),
        regex_match('.*ERROR.*', stderr.replace('\n', ' '))
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

        sleep(0.3)
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
        sleep(0.3)
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

                sleep(0.3)

            def __del__(self):
                remove(test_file)

        t = Loop()
        thread(
            threader=t,
            d={'run': TestProc(), 'method': 'start'},
            desc=desc,
        )
        t.start()

        sleep(0.3)
        assert Path(test_file).is_file()
        t.stop()
        del t
        sleep(0.3)
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

        sleep(0.3)
        del t
        assert isinstance(tl, list)
        assert len(tl) == 1
        assert isinstance(tl[0], dict)

    def test_thread_reload(self):
        test_file = f'/tmp/{time()}'
        desc = 'TestThread_5'

        class TestProc:
            @staticmethod
            def start():
                print("STARTING")
                with open(test_file, 'w+') as f:
                    f.write('test')

                sleep(1)

            def __del__(self):
                try:
                    remove(test_file)

                except FileNotFoundError:
                    pass

        t = Loop()
        thread(
            threader=t,
            d={'run': TestProc(), 'method': 'start'},
            desc=desc,
        )
        t.start()

        sleep(0.3)
        assert Path(test_file).is_file()
        remove(test_file)
        assert not Path(test_file).is_file()
        assert t.reload_thread(description=desc)
        sleep(0.3)
        assert Path(test_file).is_file()
        del t

    def test_process_basic(self, capsys):
        test_file = f'/tmp/{time()}'
        subprocess(cmd=f'touch {test_file}')
        assert Path(test_file).is_file()
        assert not process_error(capsys)
        subprocess(cmd=[f'rm {test_file}'])
        assert not Path(test_file).is_file()
        assert not process_error(capsys)

    def test_process_stdout(self, capsys):
        test_file = f'/tmp/{time()}'
        test_string = 'fa9u3lowkw3h8rh'
        subprocess(cmd=f"echo '{test_string}' > {test_file}")
        assert Path(test_file).is_file()
        assert not process_error(capsys)
        o = subprocess(cmd=[f'cat {test_file}'])
        assert o == test_string
        assert not process_error(capsys)
        remove(test_file)

    def test_process_failure(self, capsys):
        subprocess(cmd=[f'rm /tmp/doesNotExist.raaaaaandoooommm'])
        assert process_error(capsys)
