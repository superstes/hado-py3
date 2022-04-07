# Test config-related functions

from os import rename, getcwd
from pathlib import Path
from re import match as regex_match
import pytest


def mock_paths(mocker) -> dict:
    from hado.core.config.defaults import HARDCODED
    h = HARDCODED.copy()
    h['PATH_CONFIG'] = f"{getcwd()}/../etc"
    h['PATH_PLUGIN'] = f"{getcwd()}/../test/data/plugin"
    mocker.patch('hado.core.config.defaults.HARDCODED', h)
    return h


def yaml_test_validation(c, e: dict):
    stdout, _ = c.readouterr()
    o = stdout.replace('\n', ' ')

    if '_TEST_STDOUT' in e:
        assert regex_match(f".*{e['_TEST_STDOUT']}.*", o)

    else:
        assert stdout == ''

    if '_TEST_NSTDOUT' in e:
        assert not regex_match(f".*{e['_TEST_NSTDOUT']}.*", o)


class TestConfigLoader:
    def test_dump_defaults(self, mocker):
        h = mock_paths(mocker)
        mocker.patch('hado.core.config.dump.HARDCODED', h)
        from hado.core.config.dump import dump_defaults
        file = f"{h['PATH_CONFIG']}/{h['FILE_CONFIG_ENGINE_DEFAULTS']}"

        dump_defaults()
        assert Path(file).is_file()

        # for convenience
        rename(file, f'{file}.test-passed.yml')

    @pytest.mark.parametrize('item, data, result', [
        ('DEBUG', 'ok', False),  # wrong_type
        ('DEBUG', False, True),  # bool_ok
        ('PROCESS_TIMEOUT_MONITORING', '3', True),  # int_as_string
        ('PROCESS_TIMEOUT_MONITORING', '?', False),  # str_not_int
        ('PROCESS_TIMEOUT_MONITORING', 9000, False),  # int_too_high
        ('PROCESS_TIMEOUT_MONITORING', 0, False),  # int_too_low
        ('PROCESS_TIMEOUT_MONITORING', 10, True),  # int_ok
        ('DEFAULT_RESOURCE_MODE', 'nope', False),  # list_nok
        ('DEFAULT_RESOURCE_MODE', 'as', True),  # list_ok
        ('API_VIEW_PWD', 'aaaa©aaaa', False),  # invalid chars in pwd
        ('API_VIEW_PWD', 'aaa', False),  # password too short
        ('API_VIEW_USER', '', False),  # user too short
        ('API_VIEW_USER', 'a' * 21, False),  # user too long
        ('API_LISTEN_IP', 'a', False),  # invalid ip
        ('API_LISTEN_IP', '192.168.0.1', True),  # valid ipv4
        ('API_LISTEN_IP', 'fd00:dc63:8397:10bb::1', True),  # valid ipv6
    ])
    def test_validator(self, item, data, result):
        from hado.core.config.validate import validate
        assert validate(item=item, data=data) is result

    def test_check_config_engine(self, mocker):
        mock_paths(mocker)
        from hado.core.config import shared
        from hado.core.config.load import DeserializeConfig

        assert DeserializeConfig(config_ha={}, config_engine=shared.CONFIG_ENGINE)._check_engine() is True
        shared.CONFIG_ENGINE['DEBUG'] = 'nope'
        assert DeserializeConfig(config_ha={}, config_engine=shared.CONFIG_ENGINE)._check_engine() is False
        shared.CONFIG_ENGINE['DEBUG'] = False

    def test_check_config_ha(self, capsys, mocker):
        mock_paths(mocker)
        from yaml import safe_load as yaml_load
        from hado.core.config import shared
        from hado.core.config.load import DeserializeConfig

        with open('../test/data/config_ha_1.yml', 'r') as c:
            examples = yaml_load(c.read())

        for e in examples.values():
            capsys.readouterr()
            assert DeserializeConfig(
                config_ha=e,
                config_engine=shared.CONFIG_ENGINE,
            )._check_ha() is e['_TEST']
            yaml_test_validation(c=capsys, e=e)

    def test_check_config_resource(self, capsys, mocker):
        mock_paths(mocker)
        from yaml import safe_load as yaml_load
        from hado.core.config import shared
        from hado.core.config.load import DeserializeConfig

        with open('../test/data/config_ha_2.yml', 'r') as c:
            examples = yaml_load(c.read())

        for k, e in examples.items():
            capsys.readouterr()
            n = f'test_ip_{k}'
            r = e['apps']['test']['resources'][n]
            assert DeserializeConfig(
                config_ha=e,
                config_engine=shared.CONFIG_ENGINE
            )._check_resource(name=n, res=r) is e['_TEST']
            yaml_test_validation(c=capsys, e=e)

    def test_check_config_monitoring(self, capsys, mocker):
        mock_paths(mocker)
        from yaml import safe_load as yaml_load
        from hado.core.config import shared
        from hado.core.config.load import DeserializeConfig

        with open('../test/data/config_ha_3.yml', 'r') as c:
            examples = yaml_load(c.read())

        for k, e in examples.items():
            capsys.readouterr()
            n = f'test_ping_{k}'
            m = e['apps']['test']['monitoring'][n]
            assert DeserializeConfig(
                config_ha=e, config_engine=shared.CONFIG_ENGINE
            )._check_monitoring(name=n, mon=m) is e['_TEST']
            yaml_test_validation(c=capsys, e=e)

    def test_check_config_peer(self, capsys, mocker):
        mock_paths(mocker)
        from yaml import safe_load as yaml_load
        from hado.core.config import shared
        from hado.core.config.load import DeserializeConfig

        with open('../test/data/config_ha_4.yml', 'r') as c:
            examples = yaml_load(c.read())

        for k, e in examples.items():
            capsys.readouterr()
            n = f'test_peer_{k}'
            p = e[n]
            assert DeserializeConfig(
                config_ha=e, config_engine=shared.CONFIG_ENGINE
            )._check_peer(name=n, peer=p) is e['_TEST']
            yaml_test_validation(c=capsys, e=e)

    def test_check_config_app(self, capsys, mocker):
        mock_paths(mocker)
        from yaml import safe_load as yaml_load
        from hado.core.config import shared
        from hado.core.config.load import DeserializeConfig

        with open('../test/data/config_ha_5.yml', 'r') as c:
            examples = yaml_load(c.read())

        for k, e in examples.items():
            capsys.readouterr()
            n = f'test_app_{k}'
            a = e['apps'][n]
            assert DeserializeConfig(
                config_ha=e, config_engine=shared.CONFIG_ENGINE
            )._check_app(name=n, app=a) is e['_TEST']
            yaml_test_validation(c=capsys, e=e)

    def test_check_config_loader(self, capsys, mocker):
        mock_paths(mocker)
        from yaml import safe_load as yaml_load
        from hado.core.config import shared
        from hado.core.config.load import DeserializeConfig

        with open('../test/data/config_ha_6.yml', 'r') as c:
            examples = yaml_load(c.read())

        for e in examples.values():
            cnf = {}
            capsys.readouterr()

            mocker.patch('hado.core.app.App.init_resources', return_value=None)
            mocker.patch('hado.core.plugin.monitoring.SystemMonitoring.__init__', return_value=None)

            try:
                cnf = DeserializeConfig(config_ha=e, config_engine=shared.CONFIG_ENGINE).get()
                yaml_test_validation(c=capsys, e=e)

            except ValueError:
                assert e['_TEST'] is False

            assert ('apps' in cnf) is e['_TEST']

            if 'apps' in cnf:
                assert (len(cnf['apps']) > 0) is e['_TEST']
