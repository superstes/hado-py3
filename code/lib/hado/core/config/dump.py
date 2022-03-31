from hado.core.config.defaults import ENGINE, HARDCODED
from hado.core.config.validate import validate


def dump_defaults() -> None:
    lines = []
    for s, v in ENGINE.items():
        t = validate(item=s)
        ts = '' if t in [None, 'unconfigured'] else f"  # valid if => {t}"
        lines.append(f"{s}: {v}{ts}\n")

    with open(f"{HARDCODED['PATH_CONFIG']}/{HARDCODED['FILE_CONFIG_ENGINE_DEFAULTS']}", 'w+') as dump:
        dump.write(HARDCODED['FILE_CONFIG_ENGINE_DEFAULTS_COMMENT'])
        dump.writelines(lines)
