# Test config-related functions

import pytest
from os import getcwd, path, rename
from re import match as regex_match


def mock_paths(mocker) -> dict:
    from hado.core.config.defaults import HARDCODED
    h = HARDCODED.copy()
    h['PATH_CONFIG'] = f"{getcwd()}/../etc"
    h['PATH_PLUGIN'] = f"{getcwd()}/../plugin"
    mocker.patch('hado.core.config.defaults.HARDCODED', h)
    return h


def yaml_test_validation(c, e: dict):
    out, err = c.readouterr()

    if '_TEST_STDOUT' in e:
        assert regex_match(e['_TEST_STDOUT'], out)

    else:
        assert out == ''

    if '_TEST_NSTDOUT' in e:
        assert not regex_match(e['_TEST_NSTDOUT'], out)


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

    def test_check_config_ha(self, capfd, mocker):
        mock_paths(mocker)
        from yaml import safe_load as yaml_load
        from hado.core.config.load import DeserializeConfig

        with open('../test/data/config_ha_1.yml', 'r') as c:
            examples = yaml_load(c.read())

        for e in examples.values():
            assert DeserializeConfig(config_ha=e, config_engine={})._check_ha() is e['_TEST']
            yaml_test_validation(c=capfd, e=e)

    def test_check_config_resource(self, capfd, mocker):
        mock_paths(mocker)
        from yaml import safe_load as yaml_load
        from hado.core.config.shared import CONFIG_ENGINE
        from hado.core.config.load import DeserializeConfig

        with open('../test/data/config_ha_2.yml', 'r') as c:
            examples = yaml_load(c.read())

        for e in examples.values():
            n = 'test_ip'
            r = e['apps']['test']['resources'][n]
            assert DeserializeConfig(config_ha=e, config_engine=CONFIG_ENGINE)._check_resource(name=n, res=r) is e['_TEST']
            yaml_test_validation(c=capfd, e=e)

    def test_check_config_monitoring(self, capfd, mocker):
        mock_paths(mocker)
        from yaml import safe_load as yaml_load
        from hado.core.config.shared import CONFIG_ENGINE
        from hado.core.config.load import DeserializeConfig

        with open('../test/data/config_ha_3.yml', 'r') as c:
            examples = yaml_load(c.read())

        for e in examples.values():
            n = 'test_ping'
            m = e['apps']['test']['monitoring'][n]
            assert DeserializeConfig(config_ha=e, config_engine=CONFIG_ENGINE)._check_monitoring(name=n, mon=m) is e['_TEST']
            yaml_test_validation(c=capfd, e=e)
