# testing utility functions

from time import sleep

from hado.util.threader import Loop
from hado.util.helper import tcp_ping

WAIT = 0.2


class TestUtil:
    def test_tcp_ping(self):
        from http.server import HTTPServer, BaseHTTPRequestHandler
        port = 39512

        # pylint: disable=W0613
        def test_srv(data: None):
            srv = HTTPServer(('127.0.0.1', port), BaseHTTPRequestHandler)
            srv.timeout = 3
            while True:
                srv.handle_request()

        t = Loop()
        t.add_thread(
            sleep=0.1,
            thread_data={},
            description='Test Server',
            once=True,
            execute=test_srv
        )
        t.start()
        sleep(WAIT)

        assert tcp_ping(
            host='127.0.0.1',
            port=port,
        )

        t.stop()
        sleep(WAIT)

        assert not tcp_ping(
            host='127.0.0.1',
            port=port + 1,
        )
