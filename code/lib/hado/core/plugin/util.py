from pathlib import Path
from yaml import safe_load as yaml_load

from hado.core.plugin.driver import plugin_desc, plugin_cmds
from hado.core.config.defaults import HARDCODED


def existing_plugins() -> dict:
    e = {}

    for d in plugin_desc.values():
        p = f"{HARDCODED['PATH_PLUGIN']}/{d}"
        plugins = []
        for i in Path(p).iterdir():
            if i.is_dir():
                plugins.append(i.name)

        e[d] = plugins

    return e


def plugin_config(t: str, p: str) -> dict:
    f = f"{HARDCODED['PATH_PLUGIN']}/{t}/{p}/config.yml"
    if Path(f).is_file():
        with open(f, 'r') as cnf:
            return yaml_load(cnf.read())

    return {}


def max_plugin_args(t: str, p: str) -> int:
    # max != upper limit; it's the max of the minimum required arguments
    al = [0]
    cnf = plugin_config(t=t, p=p)

    for v in plugin_cmds.values():
        for c in v:
            if c in cnf and 'args' in cnf[c]:
                al.append(int(cnf[c]['args']))

    return max(al)


def enough_args(args: str, t: str, p: str) -> bool:
    return len(args.split(' ')) >= max_plugin_args(t=t, p=p)


def supported_mode(m: str, t: str, p: str) -> tuple:
    s = False
    f = None
    cnf = plugin_config(t=t, p=p)

    if 'modes' in cnf:
        if 'valid' in cnf['modes'] and m in cnf['modes']['valid']:
            s = True

        if 'fallback' in cnf['modes']:
            f = cnf['modes']['fallback']

    else:
        # no validation supported
        s = True

    return s, f
