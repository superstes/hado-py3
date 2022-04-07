# handles plugin interaction
#   hado ichimonji

from enum import Enum
from pathlib import Path
from yaml import safe_load as yaml_load

from hado.util.process import subprocess
from hado.util.debug import log
from hado.core.config.defaults import HARDCODED
from hado.core.config import shared


class PluginType(Enum):
    monitoring = 1
    resource = 2


plugin_desc = {
    PluginType.monitoring: 'monitoring',
    PluginType.resource: 'resource',
}

plugin_cmds = {
    PluginType.monitoring: ['check'],
    PluginType.resource: [
        'start', 'stop', 'active', 'other', 'init',
        'fix', 'promote', 'demote', 'leader'
        # NOTE: 'restart' and 'leave' are special cases and not directly mapped
    ]
}

plugin_cmd_timeouts = {
    'PROCESS_TIMEOUT_ACTION': ['start', 'stop', 'init', 'fix', 'promote', 'demote'],
    'PROCESS_TIMEOUT_MONITORING': ['active', 'other', 'leader', 'check'],
}


class Plugin:
    def __init__(self, plugin_type: PluginType, name: str, args: (str, list)):
        self.BASE = f"{HARDCODED['PATH_PLUGIN']}/{plugin_desc[plugin_type]}/{name}"
        self.NAME = name
        self.TYPE = plugin_type
        self.CONFIG_FILE = f"{self.BASE}/config.yml"
        self.CONFIG = {}
        self.log_id = f"Plugin - {plugin_desc[self.TYPE].capitalize()} {self.NAME} -"
        if isinstance(args, list):
            self.ARGS = args

        else:
            log(
                f"{self.log_id} Plugin arguments should be provided as list!",
                lv=3
            )
            self.ARGS = args.split(' ')

        self._load_config()
        self.CMDS = self._get_available_cmds()
        self._cached_cmds = {}

    def _load_config(self):
        if not Path(self.BASE).is_dir():
            raise NotADirectoryError(
                f"ERROR: {self.log_id} Plugin directory was not found: '{self.BASE}'"
            )

        elif Path(self.CONFIG_FILE).is_file():
            with open(self.CONFIG_FILE, 'r') as cnf:
                self.CONFIG = yaml_load(cnf.read())

        else:
            raise ValueError(
                f"ERROR: {self.log_id} Unable to load config from file: '{self.CONFIG_FILE}'"
            )

    def _get_available_cmds(self) -> list:
        cl = []
        for cmd in plugin_cmds[self.TYPE]:
            if cmd in self.CONFIG:
                cl.append(cmd)

        return cl

    def _check_cmd_support(self, t: str, s: int = 2) -> bool:
        if t not in self._cached_cmds:  # already checked
            if t in self.CMDS:
                return True

            elif s == 1:
                raise ValueError(f"ERROR: {self.log_id} Command type '{t}' not supported!")

            elif s == 2:
                log(f"{self.log_id} Command type '{t}' not supported!", lv=2)

            elif s == 3:
                log(f"{self.log_id} Command type '{t}' not supported!", lv=4)

            return False

        return True

    def _check_build_cmd(self, t: str) -> list:
        cnf_exec = self.CONFIG[t]['exec']

        if not isinstance(cnf_exec, list):
            # if single executable => accept as list
            if len(cnf_exec.split(' ', 1)) == 1:
                cnf_exec = [cnf_exec]

            else:
                log(
                    f"{self.log_id} Plugin executable should be provided as list!",
                    lv=3
                )

        if isinstance(cnf_exec, list):
            # only supporting magic on listed arguments
            cmd = cnf_exec
            if len(cmd) == 1:
                if cmd[0].find('/') == -1:
                    cmd[0] = f"{self.BASE}/{cmd[0]}"

            else:
                if cmd[1].find('/') == -1:
                    cmd[1] = f"{self.BASE}/{cmd[1]}"

        else:
            cmd = [cnf_exec]

        for part in cmd:
            for f in part.split(' '):
                if f.strip().startswith('/'):
                    if not Path(f).is_file():
                        raise FileNotFoundError(
                            f"ERROR: {self.log_id} Executable "
                            f"was not found: '{f}'"
                            )

        return cmd

    def _get_cmd(self, t: str) -> list:
        # using a cmd-cache as it won't change at runtime
        if t not in self._cached_cmds:
            _cmd = self._check_build_cmd(t=t)
            _cmd.extend(self.ARGS)
            self._cached_cmds[t] = _cmd

        if 'args' in self.CONFIG[t]:
            cnf_arg_nr = self.CONFIG[t]['args']

        else:
            cnf_arg_nr = 0

        if len(self.ARGS) < cnf_arg_nr:
            raise ValueError(
                f"ERROR: {self.log_id} Not enough arguments provided: "
                f"configured {cnf_arg_nr} / got {len(self.ARGS)}!"
            )

        log(f"{self.log_id} Executing action '{t}': '{' '.join(self._cached_cmds[t])}'", lv=4)
        return self._cached_cmds[t]

    def _exec_check(self, t: str, check: dict) -> bool:
        run = True
        if 'other' in check and 'other' in self.CMDS:
            c = check['other']
            s = self.is_other
            msg = {True: 'other node inactive', False: 'other node is active'}

            if s is not c:
                log(f"{self.log_id} {msg[c]} - not executing '{t}'!", lv=2)
                run = False

        if 'active' in check and 'active' in self.CMDS:
            c = check['active']
            s = self.is_active
            msg = {True: 'is inactive', False: 'is active'}

            if s is not c:
                log(f"{self.log_id} {msg[c]} - not executing '{t}'!", lv=2)
                run = False

        if 'leader' in check and 'leader' in self.CMDS:
            c = check['leader']
            s = self.is_leader
            msg = {True: 'is not leader', False: 'is leader'}

            if s is not c:
                log(f"{self.log_id} {msg[c]} - not executing '{t}'!", lv=2)
                run = False

        return run

    def _exec(self, t: str, check: dict = None) -> str:
        if check is None:
            check = {}

        if self._exec_check(t=t, check=check):
            shell = False
            if 'shell' in self.CONFIG[t]:
                shell = self.CONFIG[t]['shell']

            error_expected = False
            timeout = shared.CONFIG_ENGINE['PROCESS_TIMEOUT_MONITORING']
            if t in plugin_cmd_timeouts['PROCESS_TIMEOUT_MONITORING']:
                error_expected = True

            else:
                timeout = shared.CONFIG_ENGINE['PROCESS_TIMEOUT_ACTION']

            result = subprocess(
                cmd=self._get_cmd(t=t),
                shell=shell,
                error_expected=error_expected,
                timeout=timeout,
            )

        else:
            result = '0'

        log(f"{self.log_id} execution result for action '{t}': {result}", lv=4)
        return result

    def start(self) -> bool:
        # start resource
        t = 'start'
        if self._check_cmd_support(t=t, s=1):
            log(f"{self.log_id} Starting!", lv=3)
            self._exec(t=t, check={'other': False, 'active': False})
            return True

        return False

    def stop(self) -> bool:
        # stop resource
        t = 'stop'
        if self._check_cmd_support(t=t, s=1):
            log(f"{self.log_id} Stopping!", lv=2)
            self.demote()
            self._exec(t=t, check={'active': True})
            return True

        return False

    def restart(self) -> bool:
        start = False
        stop = self.stop()

        if stop:
            start = self.start()

        return all([stop, start])

    def promote(self, multi: bool = False) -> bool:
        # promote resource to cluster leader
        t = 'promote'
        c = {'leader': False}

        if not multi:
            c['other'] = False

        if self._check_cmd_support(t=t, s=2):
            log(f"{self.log_id} Promoting to leader!", lv=3)
            self._exec(t=t, check=c)
            return True

        return False

    def demote(self) -> bool:
        # demote resource to cluster worker
        t = 'demote'
        if self._check_cmd_support(t=t, s=3):
            log(f"{self.log_id} Demoting to worker!", lv=3)
            self._exec(t=t, check={'leader': True})
            return True

        return False

    def init(self) -> bool:
        # initialize resource
        t = 'init'
        if self._check_cmd_support(t=t, s=3):
            log(f"{self.log_id} Initializing!", lv=3)
            self._exec(t=t)
            return True

        return False

    def fix(self) -> bool:
        # you expect some error to occur from time to time and want to auto-'hotfix' it
        t = 'fix'
        if self._check_cmd_support(t=t, s=3):
            log(f"{self.log_id} Running fix!", lv=2)
            self._exec(t, check={'active': False})
            return True

        return False

    def _stdout_ok(self, stdout: str) -> bool:
        if stdout == "1":
            return True

        elif stdout != "0":
            log(
                f"{self.log_id} Got unexpected result from execution "
                f"(expected '0' or '1'): '{stdout}'", lv=2
            )

        return False

    def check(self) -> bool:
        # if monitoring check passed
        t = 'check'
        if self._check_cmd_support(t=t, s=1):
            log(f"{self.log_id} running monitoring task.", lv=4)
            return self._stdout_ok(self._exec(t=t))

        return False

    @property
    def is_active(self) -> (bool, None):
        # if resource is active
        t = 'active'
        if self._check_cmd_support(t=t, s=1):
            log(f"{self.log_id} checking if active.", lv=4)
            return self._stdout_ok(self._exec(t=t))

        return None

    @property
    def is_other(self) -> (bool, None):
        # check if resource is active on another node
        t = 'other'
        if self._check_cmd_support(t=t, s=3):
            log(f"{self.log_id} checking if other is active.", lv=4)
            return self._stdout_ok(self._exec(t=t))

        return None

    @property
    def is_leader(self) -> (bool, None):
        # check if this node is the leader in a resource cluster
        t = 'leader'
        if self._check_cmd_support(t=t, s=3):
            log(f"{self.log_id} checking leader state.", lv=4)
            return self._stdout_ok(self._exec(t=t))

        return None

    def __repr__(self):
        return f"HA-DO PLUGIN: {self.__dict__}"


class BasePluginUse:
    def __init__(self, vital: bool, plugin: Plugin):
        self.vital = vital
        self.plugin = plugin
        self.status = None

    def _set_attr(self, data: dict, attr: str):
        if attr in data:
            setattr(self, attr, data[attr])
