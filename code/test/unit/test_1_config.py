# Test config-related functions

from os import path, rename
from re import match as regex_match
import pytest

from .util import mock_paths


def yaml_test_validation(c, e: dict):
    stdout, _ = c.readouterr()
    o = stdout.replace('\n', ' ')

    if '_TEST_STDOUT' in e:
        assert regex_match(e['_TEST_STDOUT'], o)

    else:
        assert stdout == ''

    if '_TEST_NSTDOUT' in e:
        assert not regex_match(e['_TEST_NSTDOUT'], o)


class TestConfigLoader:
    def test_dump_defaults(self, mocker):
        h = mock_paths(mocker)
        from hado.core.config.dump import dump_defaults
        file = f"{h['PATH_CONFIG']}/{h['FILE_CONFIG_ENGINE_DEFAULTS']}"

        dump_defaults()
        assert path.isfile(file)

        rename(file, f'{file}.test-passed.yml')

    @pytest.mark.parametrize('item, data, result', [
        ('TRACEBACK_LINES', None, 'unconfigured'),  # no_data
        ('DEBUG', 'ok', False),  # wrong_type
        ('DEBUG', False, True),  # bool_ok
        ('PROCESS_TIMEOUT_MONITORING', '3', True),  # int_as_string
        ('PROCESS_TIMEOUT_MONITORING', '?', False),  # str_not_int
        ('PROCESS_TIMEOUT_MONITORING', 9000, False),  # int_too_high
        ('PROCESS_TIMEOUT_MONITORING', 0, False),  # int_too_low
        ('PROCESS_TIMEOUT_MONITORING', 10, True),  # int_ok
        ('DEFAULT_RESOURCE_MODE', 'nope', False),  # list_nok
        ('DEFAULT_RESOURCE_MODE', 'as', True),  # list_ok
    ])
    def test_validator(self, item, data, result):
        from hado.core.config.validate import validate
        assert validate(item=item, data=data) is result

    def test_check_config_engine(self, mocker):
        mock_paths(mocker)
        from hado.core.config.shared import CONFIG_ENGINE
        from hado.core.config.load import DeserializeConfig

        assert DeserializeConfig(config_ha={}, config_engine=CONFIG_ENGINE)._check_engine() is True
        CONFIG_ENGINE['DEBUG'] = 'nope'
        assert DeserializeConfig(config_ha={}, config_engine=CONFIG_ENGINE)._check_engine() is False
        CONFIG_ENGINE['DEBUG'] = False

    def test_check_config_ha(self, capsys, mocker):
        mock_paths(mocker)
        from yaml import safe_load as yaml_load
        from hado.core.config.load import DeserializeConfig

        with open('../test/data/config_ha_1.yml', 'r') as c:
            examples = yaml_load(c.read())

        for e in examples.values():
            capsys.readouterr()
            assert DeserializeConfig(config_ha=e, config_engine={})._check_ha() is e['_TEST']
            yaml_test_validation(c=capsys, e=e)

    def test_check_config_resource(self, capsys, mocker):
        mock_paths(mocker)
        from yaml import safe_load as yaml_load
        from hado.core.config.shared import CONFIG_ENGINE
        from hado.core.config.load import DeserializeConfig

        with open('../test/data/config_ha_2.yml', 'r') as c:
            examples = yaml_load(c.read())

        for k, e in examples.items():
            capsys.readouterr()
            n = f'test_ip_{k}'
            r = e['apps']['test']['resources'][n]
            assert DeserializeConfig(
                config_ha=e,
                config_engine=CONFIG_ENGINE
            )._check_resource(name=n, res=r) is e['_TEST']
            yaml_test_validation(c=capsys, e=e)

    def test_check_config_monitoring(self, capsys, mocker):
        mock_paths(mocker)
        from yaml import safe_load as yaml_load
        from hado.core.config.shared import CONFIG_ENGINE
        from hado.core.config.load import DeserializeConfig

        with open('../test/data/config_ha_3.yml', 'r') as c:
            examples = yaml_load(c.read())

        for k, e in examples.items():
            capsys.readouterr()
            n = f'test_ping_{k}'
            m = e['apps']['test']['monitoring'][n]
            assert DeserializeConfig(
                config_ha=e, config_engine=CONFIG_ENGINE
            )._check_monitoring(name=n, mon=m) is e['_TEST']
            yaml_test_validation(c=capsys, e=e)

    def test_check_config_peer(self, capsys, mocker):
        mock_paths(mocker)
        from yaml import safe_load as yaml_load
        from hado.core.config.shared import CONFIG_ENGINE
        from hado.core.config.load import DeserializeConfig

        with open('../test/data/config_ha_4.yml', 'r') as c:
            examples = yaml_load(c.read())

        for k, e in examples.items():
            capsys.readouterr()
            n = f'test_peer_{k}'
            p = e['apps']['test']['peers'][n]
            assert DeserializeConfig(
                config_ha=e, config_engine=CONFIG_ENGINE
            )._check_peer(name=n, peer=p) is e['_TEST']
            yaml_test_validation(c=capsys, e=e)

    def test_check_config_app(self, capsys, mocker):
        mock_paths(mocker)
        from yaml import safe_load as yaml_load
        from hado.core.config.shared import CONFIG_ENGINE
        from hado.core.config.load import DeserializeConfig

        with open('../test/data/config_ha_5.yml', 'r') as c:
            examples = yaml_load(c.read())

        for k, e in examples.items():
            capsys.readouterr()
            n = f'test_app_{k}'
            a = e['apps'][n]
            assert DeserializeConfig(
                config_ha=e, config_engine=CONFIG_ENGINE
            )._check_app(name=n, app=a) is e['_TEST']
            yaml_test_validation(c=capsys, e=e)

    def test_check_config_loader(self, capsys, mocker):
        mock_paths(mocker)
        from yaml import safe_load as yaml_load
        from hado.core.config.shared import CONFIG_ENGINE
        from hado.core.config.load import DeserializeConfig

        with open('../test/data/config_ha_6.yml', 'r') as c:
            examples = yaml_load(c.read())

        for e in examples.values():
            cnf = {}
            capsys.readouterr()

            # mocking 'app' so that the test is not reaching too deep
            mocker.patch('hado.core.app.App.__init__', return_value=None)

            try:
                cnf = DeserializeConfig(config_ha=e, config_engine=CONFIG_ENGINE).get()
                yaml_test_validation(c=capsys, e=e)

            except ValueError:
                assert e['_TEST'] is False

            assert ('apps' in cnf) is e['_TEST']

            if 'apps' in cnf:
                assert (len(cnf['apps']) > 0) is e['_TEST']
