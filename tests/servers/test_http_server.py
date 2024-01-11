import time
import unittest
import requests

import dxlib as dx


class TestHTTPServer(unittest.TestCase):
    def setUp(self):
        self.server = dx.servers.HTTPServer(logger=dx.InfoLogger())

    def test_start(self):
        self.server.start()
        self.assertTrue(self.server.alive)

    def test_stop(self):
        self.server.start()
        self.server.stop()
        self.assertFalse(self.server.alive)

    def test_get(self):
        self.server.start()
        response = requests.get(f"http://localhost:{self.server.port}/")
        self.assertEqual(response.status_code, 200)
        time.sleep(2)

    def tearDown(self):
        self.server.stop()


if __name__ == '__main__':
    unittest.main()
