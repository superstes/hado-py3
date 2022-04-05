# runs service timers in multiple threads
# base code source: https://github.com/sankalpjonn/timeloop
# modified for use in HA-DO

# pylint: disable=R0913

from threading import Thread, Event
from datetime import timedelta
from sys import exc_info as sys_exc_info
from traceback import format_exc

from hado.util.debug import log
from hado.core.config import shared


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
            self.join(2)
            if self.is_alive():
                log(f"Unable to join thread {self.log_name}", lv=2)

        except RuntimeError:
            log(f"Got error stopping thread {self.log_name}", lv=2)
            return False

        log(f"Stopped thread {self.log_name}", lv=3)
        return True

    def run(self) -> None:
        # pylint: disable=W0703
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
            log(f"{format_exc(limit=shared.CONFIG_ENGINE['TRACEBACK_LINES'])}")

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

    def add_thread_deco(
            self, sleep: (int, float, timedelta), thread_data, description: str,
            once: bool = False, daemon: bool = True
    ):
        log(f"Adding thread for \"{description}\" with interval \"{sleep}\"", lv=4)
        self.thread_nr += 1
        if not isinstance(sleep, timedelta):
            if sleep in [0, 0.0]:
                once = True
                sleep = 10

            sleep = timedelta(seconds=sleep)

        def decorator(function):
            self.add_thread(
                sleep=sleep,
                execute=function,
                thread_data=thread_data,
                once=once,
                description=description,
                daemon=daemon,
            )
            return function

        return decorator

    def add_thread(
            self, execute, sleep: (int, float, timedelta), thread_data, description: str,
            once: bool = False, daemon: bool = True
    ):
        self.thread_nr += 1
        if not isinstance(sleep, timedelta):
            if sleep in [0, 0.0]:
                once = True
                sleep = 10

            sleep = timedelta(seconds=sleep)

        self.jobs.add(
            Workload(
                sleep=sleep,
                execute=execute,
                data=thread_data,
                loop_instance=self,
                once=once,
                description=description,
                daemon=daemon,
                name=f"Thread #{self.thread_nr}",
            )
        )

    def stop(self) -> bool:
        log('Stopping all threads', lv=3)

        job_list = list(self.jobs)
        job_count = len(job_list)
        for i in range(job_count):
            _ = job_list[i]
            self.jobs.remove(_)
            del _

        log('All threads stopped. Exiting loop', lv=3)
        if len(self.jobs) == 0:
            return True

        return False

    def stop_thread(self, description: str) -> bool:
        log(f"Stopping thread for \"{description}\"", lv=4)
        job_list = list(self.jobs)
        job_count = len(job_list)
        for i in range(job_count):
            _ = job_list[i]
            if _.description == description:
                self.jobs.remove(_)
                log(f"Thread {_.description} stopped.", lv=3)
                del _
                return True

        return False

    def start_thread(self, description: str) -> bool:
        for job in self.jobs:
            if job.description == description:
                job.start()
                log(f"Thread {job.description} started.", lv=4)
                return True

        return False

    def reload_thread(self, description: str, sleep: int = None, thread_data=None) -> bool:
        log(f"Reloading thread for \"{description}\"", lv=3)
        current_thread = self.get_thread(description=description)

        if current_thread:
            self.stop_thread(description=description)
            self.add_thread(
                execute=current_thread.execute,
                sleep=current_thread.sleep if sleep is None else sleep,
                thread_data=current_thread.data if thread_data is None else thread_data,
                description=current_thread.description if description is None else description,
            )
            self.start_thread(description=description)
            return True

        return False

    def get_thread(self, description: str) -> (Workload, None):
        for job in self.jobs:
            if job.description == description:
                return job

        return None

    def list(self) -> set:
        log('Returning thread list', lv=4)
        return self.jobs

    def __del__(self):
        self.stop()
