# process handler

from subprocess import Popen as subprocessPopen
from subprocess import PIPE as SUBPROCESS_PIPE
from subprocess import TimeoutExpired

from hado.util.debug import log
from hado.core.config.shared import CONFIG_ENGINE


def subprocess(
        cmd: (list, str),
        timeout: int = CONFIG_ENGINE['PROCESS_TIMEOUT_MONITORING'],
        shell: bool = False
) -> str:
    if not isinstance(cmd, list):
        cmd = [cmd]

    log(f"Executing command \"{cmd}\"", lv=4)
    stdout = None

    try:
        proc = subprocessPopen(
            cmd,
            shell=shell,
            stdout=SUBPROCESS_PIPE,
            stderr=SUBPROCESS_PIPE
        )
        stdout_bytes, stderr_bytes = proc.communicate(timeout=timeout)
        stdout, stderr = stdout_bytes.decode('utf-8').strip(), stderr_bytes.decode('utf-8').strip()
        exit_code = proc.returncode

    except TimeoutExpired as e:
        exit_code = 1
        stderr = e

    except FileNotFoundError as e:
        log(
            "The supplied command was not formatted as expected!\n"
            "Possible causes:\n"
            "  1. command not split-up in list,\n"
            "  2. using pipes without setting 'shell' to 'true'.\n"
        )
        exit_code = 1
        stderr = e

    if exit_code == 0 and stderr in ['', ' ', None]:
        log(f"Process output: \"{stdout}\"", lv=4)

    else:
        log(
            f"Got error while processing command {cmd}: "
            f"exit-code {exit_code} - \"{stderr}\" | output: \"{stdout}\""
        )

    return stdout
