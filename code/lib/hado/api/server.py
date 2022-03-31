from waitress import serve
from flask import Flask, abort

from hado.core.config.shared import CONFIG_ENGINE
from hado.util.debug import log
from hado.api.util import client_ip, deny_public, HTTP_STATI
from hado.api.get import api_get
from hado.api.post import api_post


api = Flask('HA-DO-RESTAPI')
api.register_blueprint(api_get)
api.register_blueprint(api_post)


def start():
    # pylint: disable=W0703
    port = CONFIG_ENGINE['API_LISTEN_PORT']
    log(f'Starting rest-server on port {port}.', lv=3)
    try:
        serve(
            app=api.wsgi_app,
            host=CONFIG_ENGINE['API_LISTEN_IP'],
            port=port,
        )

    except Exception as e:
        log(f"Rest-server died with error: '{e}'!")


@api.route('/<path:p>')
def catch_all(p):
    deny_public()
    log(f"Got access to unknown path: '{p}' from client '{client_ip()}'.", lv=4)
    abort(HTTP_STATI['NOT_FOUND'])
