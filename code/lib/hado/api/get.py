from typing import NoReturn
from flask import abort, jsonify, Blueprint, Response

from hado.core.config.shared import CONFIG_LOADED
from hado.api.util import deny_public, HTTP_STATI

# pylint: disable=R1710

api_get = Blueprint('api_get', __name__)


@api_get.route('/', methods=['GET'])
def get_whole() -> (Response, NoReturn):
    deny_public()
    return jsonify(
        CONFIG_LOADED['system'].stats | {
            'apps': [app.stats for app in CONFIG_LOADED['apps']],
        }
    )


@api_get.route('/s', methods=['GET'])
def get_system() -> (Response, NoReturn):
    deny_public()
    return jsonify(CONFIG_LOADED['system'].stats)


@api_get.route('/a/<string:app>', methods=['GET'])
def get_app(app: str) -> (Response, NoReturn):
    deny_public()
    for a in CONFIG_LOADED['apps']:
        if a.name == app:
            return jsonify(a.stats)

    abort(HTTP_STATI['NOT_FOUND'])


@api_get.route('/a/<string:app>/r/<string:res>', methods=['GET'])
def get_resource(app: str, res: str) -> (Response, NoReturn):
    deny_public()
    for a in CONFIG_LOADED['apps']:
        if a.name == app:
            for r in a.resources:
                if r.name == res:
                    return jsonify(r.stats)

    abort(HTTP_STATI['NOT_FOUND'])


@api_get.route('/a/<string:app>/m/<string:mon>', methods=['GET'])
def get_monitoring(app: str, mon: str) -> (Response, NoReturn):
    deny_public()
    for a in CONFIG_LOADED['apps']:
        if a.name == app:
            for m in a.monitoring:
                if m.name == mon:
                    return jsonify(m.stats)

    abort(HTTP_STATI['NOT_FOUND'])


@api_get.route('/d', methods=['GET'])
def get_debug() -> (Response, NoReturn):
    deny_public()
    # todo: basic auth for debug config-dump
    abort(HTTP_STATI['NOT_IMPL'])
