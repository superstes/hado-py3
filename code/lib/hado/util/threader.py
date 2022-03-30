# runs service timers in multiple threads
# base code source: https://github.com/sankalpjonn/timeloop
# modified for use in HA-DO

# pylint: disable=W0702, R0913

from threading import Thread, Event
from time import sleep as time_sleep
from datetime import timedelta
from sys import exc_info as sys_exc_info
from traceback import format_exc

from hado.util.debug import log
from hado.core.config.shared import CONFIG_ENGINE


class Workload(Thread):
    def __init__(
            self, sleep: timedelta, execute, data, loop_instance, name: str,
            description: str, once: bool = False, daemon: bool = True
    ):
        Thread.__init__(self, daemon=daemon, name=name)
        self.sleep = sleep
        self.execute = execute  # function to execute
        self.data = data
        self.loop_instance = loop_instance
        self.once = once
        self.state_stop = Event()
        self.description = description
        self.log_name = f"\"{self.name}\" (\"{description}\")"

    def stop(self) -> bool:
        log(f"Thread stopping {self.log_name}", lv=3)
        self.state_stop.set()

        try:
            self.join(CONFIG_ENGINE['PROCESS_TIMEOUT'])
            if self.is_alive():
                log(f"Unable to join thread {self.log_name}", lv=2)

        except RuntimeError:
            log(f"Got error stopping thread {self.log_name}", lv=2)
            return False

        log(f"Stopped thread {self.log_name}", lv=3)
        return True

    def run(self) -> None:
        log(f"Entering runtime of thread {self.log_name}", lv=4)
        try:
            if self.once:
                while not self.state_stop.wait(self.sleep.total_seconds()):
                    self.execute(data=self.data)
                    Loop.stop_thread(self.loop_instance, description=self.description)
                    break

            else:
                while not self.state_stop.wait(self.sleep.total_seconds()):
                    if self.state_stop.isSet():
                        log(f"Exiting thread {self.log_name}", lv=2)
                        break

                    else:
                        log(f"Starting thread {self.log_name}", lv=4)
                        self.execute(data=self.data)

        except Exception as e:
            exc_type, _, _ = sys_exc_info()
            log(f"Thread {self.log_name} failed with error: \"{exc_type} - {e}\"")
            log(f"{format_exc(limit=CONFIG_ENGINE['TRACEBACK_LINES'])}")

            if not self.once:
                self.run()


class Loop:
    def __init__(self):
        self.jobs = set()
        self.thread_nr = 0

    def start(self) -> None:
        log('Starting all threads', lv=4)

        for job in self.jobs:
            job.start()

    def add_thread(
            self, sleep_time: int, thread_data, description: str,
            once: bool = False, daemon: bool = True
    ):
        log(f"Adding thread for \"{description}\" with interval \"{sleep_time}\"", lv=4)
        self.thread_nr += 1

        def decorator(function):
            if sleep_time == 0:
                sleep_time_new = 10
                self.jobs.add(
                    Workload(
                        sleep=timedelta(seconds=sleep_time_new),
                        execute=function,
                        data=thread_data,
                        loop_instance=self,
                        once=True,
                        description=description,
                        daemon=daemon,
                        name=f"Thread #{self.thread_nr}",
                    )
                )
            else:
                self.jobs.add(
                    Workload(
                        sleep=timedelta(seconds=sleep_time),
                        execute=function,
                        data=thread_data,
                        loop_instance=self,
                        once=once,
                        description=description,
                        daemon=daemon,
                        name=f"Thread #{self.thread_nr}",
                    )
                )
            return function
        return decorator

    def _block_root_process(self) -> None:
        while True:
            try:
                time_sleep(1)

            except KeyboardInterrupt:
                self.stop()

    def stop(self) -> bool:
        log('Stopping all threads', lv=3)

        for job in self.jobs:
            job.stop()

        log('All threads stopped. Exiting loop', lv=3)
        return True

    def stop_thread(self, description: str):
        log(f"Stopping thread for \"{description}\"", lv=4)
        for job in self.jobs:
            if job.description == description:
                job.stop()
                self.jobs.remove(job)
                log(f"Thread {job.description} stopped.", lv=3)
                del job
                break

    def start_thread(self, description: str) -> None:
        for job in self.jobs:
            if job.description == description:
                job.start()
                log(f"Thread {job.description} started.", lv=4)
                break

    def reload_thread(self, sleep_time: int, thread_data, description: str) -> None:
        log(f"Reloading thread for \"{description}\"", lv=3)
        self.stop_thread(description=description)
        self.add_thread(
            sleep_time=sleep_time,
            thread_data=thread_data,
            description=description,
        )
        self.start_thread(description=description)

    def list(self) -> list:
        log('Returning thread list', lv=4)
        return [job.data for job in self.jobs]
