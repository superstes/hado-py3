from flask_httpauth import HTTPBasicAuth

from hado.core.config import shared
from hado.util.debug import log

auth = HTTPBasicAuth()

users = {
    shared.CONFIG_ENGINE['API_SYNC_USER']: shared.CONFIG_ENGINE['API_SYNC_PWD'],
    shared.CONFIG_ENGINE['API_VIEW_USER']: shared.CONFIG_ENGINE['API_VIEW_PWD'],
}


@auth.verify_password
def verify_password(username, password) -> (str, None):
    if username in users and users[username] == password:
        log(f"Rest-Server - user '{username}' authenticated successfully.", lv=4)
        return username

    log(f"Rest-Server - failed authentication for user '{username}'!", lv=2)
    return None


def auth_optional() -> bool:
    return not shared.CONFIG_ENGINE['API_AUTH']
