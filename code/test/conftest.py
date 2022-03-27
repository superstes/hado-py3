

def pytest_sessionstart():
    print('Initializing global vars for session.')
    from hado.core.config.shared import init
    init()
