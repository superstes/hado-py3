from hado.core.config.defaults import HARDCODED
from hado.core.config.defaults import ENGINE as ENGINE_DEFAULTS

# pylint: disable=C0415
# startup-fallback (before shared-vars got initialized)


def get_debug() -> bool:
    try:
        from hado.core.config import shared
        return shared.CONFIG_ENGINE['DEBUG']

    except AttributeError:
        return ENGINE_DEFAULTS['DEBUG']


def get_log_mode() -> bool:
    try:
        from hado.core.config import shared
        return shared.CONFIG_ENGINE['LOG_MODE']

    except AttributeError:
        return ENGINE_DEFAULTS['LOG_MODE']


def log(msg: str, lv: int = 1):
    cnf_ll = HARDCODED['LOG_MODE']['MAPPING'][get_log_mode()]

    if get_debug() or cnf_ll >= lv:
        print(f"{HARDCODED['LOG_MODE']['MAPPING_REV'][lv]}: {msg}")
