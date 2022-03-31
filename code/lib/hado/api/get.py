from typing import NoReturn
from flask import abort, jsonify, Blueprint, Response

from hado.core.config.shared import CONFIG_LOADED
from hado.api.util import deny_public, HTTP_STATI
from hado.api.stati import app_status, plugin_status, system_status

# pylint: disable=R1710

api_get = Blueprint('api_get', __name__)


@api_get.route('/', methods=['GET'])
def get_whole() -> (Response, NoReturn):
    deny_public()
    return jsonify({
        'system': system_status(),
        'apps': {a.name: app_status(a) for a in CONFIG_LOADED['apps']}
    })


@api_get.route('/s', methods=['GET'])
def get_system() -> (Response, NoReturn):
    deny_public()
    return jsonify(system_status())


@api_get.route('/a/<string:app>', methods=['GET'])
def get_app(app: str) -> (Response, NoReturn):
    deny_public()
    for a in CONFIG_LOADED['apps']:
        if a.name == app:
            return jsonify(app_status(a))

    abort(HTTP_STATI['NOT_FOUND'])


@api_get.route('/a/<string:app>/r/<string:res>', methods=['GET'])
def get_resource(app: str, res: str) -> (Response, NoReturn):
    deny_public()
    for a in CONFIG_LOADED['apps']:
        if a.name == app:
            for r in a.resources:
                if r.name == res:
                    return jsonify(plugin_status(r))

    abort(HTTP_STATI['NOT_FOUND'])


@api_get.route('/a/<string:app>/m/<string:mon>', methods=['GET'])
def get_monitoring(app: str, mon: str) -> (Response, NoReturn):
    deny_public()
    for a in CONFIG_LOADED['apps']:
        if a.name == app:
            for m in a.monitoring:
                if m.name == mon:
                    return jsonify(plugin_status(m))

    abort(HTTP_STATI['NOT_FOUND'])


@api_get.route('/d', methods=['GET'])
def get_debug() -> (Response, NoReturn):
    deny_public()
    # todo: basic auth for debug config-dump
    abort(HTTP_STATI['NOT_IMPL'])
