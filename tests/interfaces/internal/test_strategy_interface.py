import time
import unittest

import pandas as pd
import requests

import dxlib as dx
from dxlib import Inventory, History
from dxlib.interfaces.internal import StrategyInterface


class TestStrategyAPI(unittest.TestCase):
    class SampleStrategy(dx.Strategy):

        def execute(self, observation: any, position: Inventory, history: History) -> pd.Series:
            return pd.Series()

    def setUp(self):
        self.strategy = self.SampleStrategy()
        self.interface = StrategyInterface(self.strategy)

        self.server = dx.HTTPServer(port=8080)
        self.server.add_interface(self.interface)
        self.server.start()
        while not self.server.alive:
            time.sleep(0.1)

    def tearDown(self):
        self.server.stop()

    def testServer(self):
        self.assertEqual(self.server.alive, True)

    def testGetEndpoint(self):
        self.assertEqual(self.server.alive, True)

        response = requests.get("http://localhost:8080/")
        endpoints = response.json()

        try:
            for endpoint, func in self.interface.endpoints:
                description = endpoint.description
                params = endpoint.params
                method = endpoint.method
                route_name = endpoint.route_name

                self.assertEqual(description, endpoints[route_name][method.value]["description"])

                for name, typehint in params.items():
                    if name == "self":
                        continue
                    self.assertEqual(str(typehint), endpoints[route_name][method.value]["params"][name])

                self.assertEqual(method.name, list(endpoints[route_name].keys())[0])
                self.assertEqual(route_name, list(endpoints.keys())[0])
        except Exception as e:
            raise e


if __name__ == '__main__':
    unittest.main()
