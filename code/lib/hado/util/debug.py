from hado.core.config.shared import CONFIG_ENGINE
from hado.core.config.defaults import HARDCODED


def log(msg: str, lv: int = 1):
    cnf_ll = HARDCODED['LOG_MODE']['MAPPING'][CONFIG_ENGINE['LOG_MODE']]

    if CONFIG_ENGINE['DEBUG'] or cnf_ll >= lv:
        print(f"{HARDCODED['LOG_MODE']['MAPPING_REV'][lv]}: {msg}")
