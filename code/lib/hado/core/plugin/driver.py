# handles plugin interaction
#   hado ichimonji

from enum import Enum
from pathlib import Path
from yaml import safe_load as yaml_load

from hado.util.process import subprocess
from hado.util.debug import log
from hado.core.config.defaults import HARDCODED
from hado.core.config.shared import CONFIG_ENGINE


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
    'PROCESS_TIMEOUT_MONITORING': ['active', 'other', 'leader'],
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
        self.CMDS = self._get_cmds()

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

    def _get_cmds(self) -> list:
        cl = []
        for cmd in plugin_cmds[self.TYPE]:
            if cmd in self.CONFIG:
                cl.append(cmd)

        return cl

    def _check_cmd_support(self, t: str, s: int = 2) -> bool:
        if t in self.CMDS:
            return True

        elif s == 1:
            raise ValueError(f"ERROR: {self.log_id} Command type '{t}' not supported!")

        elif s == 2:
            log(f"{self.log_id} Command type '{t}' not supported!", lv=2)

        elif s == 3:
            log(f"{self.log_id} Command type '{t}' not supported!", lv=4)

        return False

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
                if f.find('/') != -1:
                    if not Path(f).is_file():
                        raise FileNotFoundError(
                            f"ERROR: {self.log_id} Executable "
                            f"was not found: '{f}'"
                            )

        return cmd

    def _get_cmd(self, t: str) -> list:
        cmd = self._check_build_cmd(t=t)
        cmd.extend(self.ARGS)

        if 'args' in self.CONFIG[t]:
            cnf_arg_nr = self.CONFIG[t]['args']

        else:
            cnf_arg_nr = 0

        if len(self.ARGS) < cnf_arg_nr:
            raise ValueError(
                f"ERROR: {self.log_id} Not enough arguments provided: "
                f"configured {cnf_arg_nr} / got {len(self.ARGS)}!"
            )

        log(f"{self.log_id} Executing action '{t}': '{' '.join(cmd)}'", lv=4)
        return cmd

    # pylint: disable=R0913
    def _exec(self, t: str,
              cno: bool = False,
              ca: bool = False, cna: bool = False,
              cnl: bool = False, cl: bool = False,
              ) -> str:
        run = True

        if cno and 'other' in self.CMDS:
            if self.is_other:
                log(f"{self.log_id} other node is active - not executing '{t}'!", lv=2)
                run = False

        if (ca or cna) and 'active' in self.CMDS:
            active = self.is_active
            if ca and not active:
                log(f"{self.log_id} is not active - not executing '{t}'!", lv=2)
                run = False

            if cna and active:
                log(f"{self.log_id} is active - not executing '{t}'!", lv=2)
                run = False

        if (cl or cnl) and 'leader' in self.CMDS:
            leader = self.is_leader
            if cl and not leader:
                log(f"{self.log_id} is not leader - not executing '{t}'!", lv=2)
                run = False

            if cnl and leader:
                log(f"{self.log_id} is leader - not executing '{t}'!", lv=2)
                run = False

        if run:
            shell = False
            if 'shell' in self.CONFIG[t]:
                shell = self.CONFIG[t]['shell']

            for k, v in plugin_cmd_timeouts.items():
                if t in v:
                    return subprocess(cmd=self._get_cmd(t=t), timeout=CONFIG_ENGINE[k], shell=shell)

            return subprocess(cmd=self._get_cmd(t=t), shell=shell)

        else:
            return '0'

    def start(self) -> bool:
        # start resource
        t = 'start'
        if self._check_cmd_support(t=t, s=1):
            log(f"{self.log_id} Starting!", lv=3)
            self._exec(t=t, cno=True, cna=True)
            return True

        return False

    def stop(self) -> bool:
        # stop resource
        t = 'stop'
        if self._check_cmd_support(t=t, s=1):
            log(f"{self.log_id} Stopping!", lv=2)
            self.demote()
            self._exec(t=t, ca=True)
            return True

        return False

    def restart(self) -> bool:
        start = False
        stop = self.stop()

        if stop:
            start = self.start()

        return all([stop, start])

    def promote(self) -> bool:
        # promote resource to cluster leader
        t = 'promote'
        if self._check_cmd_support(t=t, s=2):
            log(f"{self.log_id} Promoting to leader!", lv=3)
            self._exec(t=t, cnl=True)
            return True

        return False

    def demote(self) -> bool:
        # demote resource to cluster worker
        t = 'demote'
        if self._check_cmd_support(t=t, s=3):
            log(f"{self.log_id} Demoting to worker!", lv=3)
            self._exec(t=t, cl=True)
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
            self._exec(t, cna=True)
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

    @property
    def status(self):
        return self.plugin.is_active

    def _set_attr(self, data: dict, attr: str):
        if attr in data:
            setattr(self, attr, data[attr])

    @property
    def stats(self) -> dict:
        return {self.name: self.status}
