from ..core.config import CONFIG_ENGINE


def log(msg: str, prefix: str = 'ERROR'):
    if prefix != 'DEBUG' or CONFIG_ENGINE['DEBUG']:
        print(f"{prefix}: {msg}")
