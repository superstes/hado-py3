# handles plugin interaction
#   hado ichimonji

from hado.util.process import subprocess
from hado.util.debug import log

from enum import Enum
from yaml import safe_load as yaml_load
from os import path as os_path


class PluginType(Enum):
    monitoring = 1
    resource = 2


plugin_desc = {
    PluginType.monitoring: 'Monitoring',
    PluginType.resource: 'Resource',
}

plugin_cmds = {
    PluginType.monitoring: ['check'],
    PluginType.resource: ['start', 'stop', 'active', 'other', 'init', 'fix', 'promote', 'demote', 'leader']
}

plugin_cmd_timeouts = {
    'PROCESS_TIMEOUT_ACTION': ['start', 'stop', 'init', 'fix', 'promote', 'demote'],
    'PROCESS_TIMEOUT_MONITORING': ['active', 'other', 'leader'],
}


class Plugin:
    def __init__(self, plugin_type: PluginType, base: str, name: str, args: str):
        self.BASE = f"{base}/{name}"
        self.NAME = name
        self.TYPE = plugin_type
        self.ARGS = args.split(' ')
        self.CONFIG_FILE = f"{self.BASE}/config.yml"
        self.CONFIG = {}
        self._load_config()
        self.CMDS = []
        self._get_cmds()
        self.log_id = f"Plugin - {plugin_desc[self.TYPE]} {self.NAME} -"
        self._check_plugin()

    def _check_plugin(self):
        if not os_path.isdir(self.BASE):
            raise NotADirectoryError(f"ERROR: {self.log_id} Plugin directory was not found: '{self.BASE}'")

        self._get_cmds()

    def _load_config(self):
        if os_path.isfile(self.CONFIG_FILE):
            with open(self.CONFIG_FILE, 'r') as cnf:
                self.CONFIG = yaml_load(cnf.read())

        else:
            raise ValueError(f"ERROR: {self.log_id} Unable to load config from file: '{self.CONFIG_FILE}'")

    def _get_cmds(self):
        for cmd in plugin_cmds[self.TYPE]:
            if cmd in self.CONFIG:
                self.CMDS.append(cmd)

    def _check_cmd_support(self, t: str, s: int = 2) -> bool:
        if t in self.CMDS:
            return True

        elif s == 1:
            raise ValueError(f"ERROR: {self.log_id} Command type '{t}' not supported!")

        elif s == 2:
            log(f"{self.log_id} Command type '{t}' not supported!", 'WARNING')

        elif s == 3:
            log(f"{self.log_id} Command type '{t}' not supported!", 'DEBUG')

    def _get_cmd(self, t: str) -> str:
        cnf_exec = self.CONFIG[t]['exec']
        cnf_arg_nr = self.CONFIG[t]['args']
        e_args = ''
        e_bin = ''

        if len(self.ARGS) < cnf_arg_nr:
            raise ValueError(f"ERROR: {self.log_id} Not enough arguments provided: configured {cnf_arg_nr} / got {len(self.ARGS)}!")

        e = cnf_exec.split(' ', 1)

        if len(e) == 2:
            _bin = e[1]

            if not os_path.isfile(_bin):
                raise FileNotFoundError(f"ERROR: {self.log_id} Binary to execute was not found: '{_bin}'")

            e_bin = f"{e[1]} "
            e_exe = e[2]

        else:
            e_exe = e[1]

        if e_exe.find('/') == -1:
            e_exe = f"{self.BASE}/{e_exe}"

        if not os_path.isfile(e_exe):
            raise FileNotFoundError(f"ERROR: {self.log_id} Executable was not found: '{e_exe}'")

        if len(self.ARGS) > 0:
            e_args = f" {' '.join(self.ARGS)}"

        log(f"{self.log_id} Executing action '{t}': '{e_bin}{e_exe}{e_args}'", 'DEBUG')

        return f"{e_bin}{e_exe}{e_args}"

    def _exec(self, t: str,
              cno: bool = False,
              ca: bool = False, cna: bool = False,
              cnl: bool = False, cl: bool = False,
              ):
        cmd = self._get_cmd(t=t)
        run = True

        if cno and 'other' in self.CMDS:
            if self.is_other:
                log(f"{self.log_id} other node is active - not executing '{t}'!", 'WARNING')
                run = False

        if (ca or cna) and 'active' in self.CMDS:
            active = self.is_active
            if ca and not active:
                log(f"{self.log_id} is not active - not executing '{t}'!", 'WARNING')
                run = False

            if cna and active:
                log(f"{self.log_id} is active - not executing '{t}'!", 'WARNING')
                run = False

        if (cl or cnl) and 'leader' in self.CMDS:
            leader = self.is_leader
            if cl and not leader:
                log(f"{self.log_id} is not leader - not executing '{t}'!", 'WARNING')
                run = False

            if cnl and leader:
                log(f"{self.log_id} is leader - not executing '{t}'!", 'WARNING')
                run = False

        if run:
            for k, v in plugin_cmd_timeouts.items():
                if t in v:
                    return subprocess(cmd=cmd, timeout=CONFIG_ENGINE[k])

            return subprocess(cmd=cmd)

        else:
            return '0'

    def start(self):
        # start resource
        t = 'start'
        if self._check_cmd_support(t=t, s=1):
            log(f"{self.log_id} Starting!", 'INFO')
            self._exec(t, cno=True, cna=True)

    def stop(self):
        # stop resource
        t = 'stop'
        if self._check_cmd_support(t=t, s=1):
            log(f"{self.log_id} Stopping!", 'WARNING')
            self.demote()
            self._exec(t, ca=True)

    def promote(self):
        # promote resource to cluster leader
        t = 'promote'
        if self._check_cmd_support(t=t, s=2):
            log(f"{self.log_id} Promoting to leader!", 'INFO')
            self._exec(t, cnl=True)

    def demote(self):
        # demote resource to cluster worker
        t = 'demote'
        if self._check_cmd_support(t=t, s=3):
            log(f"{self.log_id} Demoting to worker!", 'INFO')
            self._exec(t, cl=True)

    def init(self):
        # initialize resource
        t = 'init'
        if self._check_cmd_support(t=t, s=3):
            log(f"{self.log_id} Initializing!", 'INFO')
            self._exec(t)

    def fix(self):
        # you expect some error to occur from time to time and want to auto-'hotfix' it
        t = 'fix'
        if self._check_cmd_support(t=t, s=3):
            log(f"{self.log_id} Running fix!", 'WARNING')
            self._exec(t, cna=True)

    def _stdout_ok(self, stdout: str) -> bool:
        if stdout == "1":
            return True

        elif stdout != "0":
            log(f"{self.log_id} Got unexpected result from execution (expected '0' or '1'): '{stdout}'", 'WARNING')

        return False

    def check(self) -> bool:
        # if monitoring check passed
        t = 'check'
        if self._check_cmd_support(t=t, s=1):
            log(f"{self.log_id} running monitoring task.", 'DEBUG')
            return self._stdout_ok(self._exec(t))

    @property
    def is_active(self) -> bool:
        # if resource is active
        t = 'active'
        if self._check_cmd_support(t=t, s=1):
            log(f"{self.log_id} checking if active.", 'DEBUG')
            return self._stdout_ok(self._exec(t))

    @property
    def is_other(self) -> bool:
        # check if resource is active on another node
        t = 'other'
        if self._check_cmd_support(t=t, s=3):
            log(f"{self.log_id} checking if other is active.", 'DEBUG')
            return self._stdout_ok(self._exec(t))

    @property
    def is_leader(self) -> bool:
        # check if this node is the leader in a resource cluster
        t = 'leader'
        if self._check_cmd_support(t=t, s=3):
            log(f"{self.log_id} checking leader state.", 'DEBUG')
            return self._stdout_ok(self._exec(t))


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
