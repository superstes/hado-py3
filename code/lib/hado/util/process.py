# process handler

from subprocess import Popen as subprocessPopen
from subprocess import PIPE as SUBPROCESS_PIPE
from subprocess import TimeoutExpired

from hado.util.debug import log
from hado.core.config.shared import CONFIG_ENGINE


def subprocess(
        cmd: (list, str),
        timeout: int = CONFIG_ENGINE['PROCESS_TIMEOUT_MONITORING']
) -> str:
    log(f"Executing command \"{cmd}\"", 'DEBUG')

    if not isinstance(cmd, list):
        cmd = [cmd]

    try:
        proc = subprocessPopen(
            cmd,
            shell=True,
            stdout=SUBPROCESS_PIPE,
            stderr=SUBPROCESS_PIPE
        )
        stdout_bytes, stderr_bytes = proc.communicate(timeout=timeout)
        stdout, stderr = stdout_bytes.decode('utf-8').strip(), stderr_bytes.decode('utf-8').strip()
        exit_code = proc.returncode

    except TimeoutExpired as error:
        stdout = None
        exit_code = 1
        stderr = error

    if exit_code == 0 and stderr in ['', ' ', None]:
        log(f"Process output: \"{stdout}\"", 'DEBUG')

    else:
        log(
            f"Got error while processing command \"{cmd}\": "
            f"exit-code {exit_code} - \"{stderr}\" | output: \"{stdout}\""
        )

    return stdout
