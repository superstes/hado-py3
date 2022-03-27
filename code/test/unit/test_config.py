# Test config-related functions

import pytest
from os import getcwd, path, rename


class TestConfigLoader:
    def test_dump_defaults(self, mocker):
        from hado.core.config.defaults import HARDCODED
        hm = HARDCODED.copy()
        hm['PATH_CONFIG'] = f"{getcwd()}/../etc"
        file = f"{hm['PATH_CONFIG']}/{hm['FILE_CONFIG_ENGINE_DEFAULTS']}"
        mocker.patch('hado.core.config.defaults.HARDCODED', hm)

        from hado.core.config.dump import dump_defaults
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

    def test_check_config_engine(self):
        from hado.core.config.shared import CONFIG_ENGINE
        from hado.core.config.load import DeserializeConfig

        assert DeserializeConfig(config_ha={}, config_engine=CONFIG_ENGINE)._check_engine() is True
        CONFIG_ENGINE['DEBUG'] = 'nope'
        assert DeserializeConfig(config_ha={}, config_engine=CONFIG_ENGINE)._check_engine() is False

    def test_check_config_ha(self, capfd):
        from hado.core.config.load import DeserializeConfig

        from yaml import safe_load as yaml_load
        with open('../test/data/config_ha_1.yml', 'r') as c:
            examples = yaml_load(c.read())

        for e in examples.values():
            assert DeserializeConfig(config_ha=e, config_engine={})._check_ha() is e['_TEST']
            out, err = capfd.readouterr()

            if '_TEST_STDOUT' in e:
                assert out.find(e['_TEST_STDOUT']) != -1

            else:
                assert out == ''

            if '_TEST_NSTDOUT' in e:
                assert out.find(e['_TEST_NSTDOUT']) == -1
