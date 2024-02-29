import json
import time
import unittest

import pandas as pd
import requests

import dxlib as dx
from dxlib.strategies import RsiStrategy


class TestExecutorInterface(unittest.TestCase):
    server = None
    strategy = None
    executor = None
    interface = None
    inventory = None
    security_manager = None

    @classmethod
    def setUpClass(cls):
        cls.strategy = RsiStrategy(window=1)

        cls.security_manager = dx.SecurityManager.from_list(["AAPL", "MSFT"])
        cls.schema = dx.Schema(
            levels=[dx.SchemaLevel.DATE, dx.SchemaLevel.SECURITY],
            fields=["close"],
            security_manager=cls.security_manager,
        )

        cls.inventory = dx.Inventory({security: 0 for security in cls.security_manager.values()})
        cls.executor = dx.Executor(cls.strategy, cls.inventory)

        cls.interface = dx.ExecutorInterface(cls.executor, url="http://localhost:8000")
        cls.server = dx.HTTPServer(port=8000)
        cls.server.add_interface(cls.interface)
        cls.server.start()

        while not cls.server.alive:
            time.sleep(0.1)

    @classmethod
    def tearDownClass(cls):
        cls.server.stop()

    def test_run(self):
        history = dx.History(
            {
                (pd.Timestamp("2021-01-01"), "AAPL"): {"close": 100},
                (pd.Timestamp("2021-01-01"), "MSFT"): {"close": 200},
                (pd.Timestamp("2021-01-02"), "AAPL"): {"close": 110},
                (pd.Timestamp("2021-01-02"), "MSFT"): {"close": 210},
                (pd.Timestamp("2021-01-03"), "AAPL"): {"close": 120},
                (pd.Timestamp("2021-01-03"), "MSFT"): {"close": 220},
            },
            self.schema,
        )

        run_params = {
            "obj": history.to_dict(serializable=True),
        }

        response = self.interface.request(route="/run", json=run_params)

        data = response["data"]

        signal_history = dx.History.from_dict(**data, serialized=True, )
        signal_dict = signal_history.to_dict()['df']

        self.assertEqual(
            signal_dict,
            {('2021-01-01T00:00:00', (('ticker', 'AAPL'), ('security_type', (('value', 'equity'),)))): {
                'signal': (('side', (('value', 0),)), ('quantity', None), ('price', None))},
             ('2021-01-01T00:00:00', (('ticker', 'MSFT'), ('security_type', (('value', 'equity'),)))): {
                 'signal': (('side', (('value', 0),)), ('quantity', None), ('price', None))},
             ('2021-01-02T00:00:00', (('ticker', 'AAPL'), ('security_type', (('value', 'equity'),)))): {
                 'signal': (('side', (('value', -1),)), ('quantity', 1), ('price', None))},
             ('2021-01-02T00:00:00', (('ticker', 'MSFT'), ('security_type', (('value', 'equity'),)))): {
                 'signal': (('side', (('value', -1),)), ('quantity', 1), ('price', None))},
             ('2021-01-03T00:00:00', (('ticker', 'AAPL'), ('security_type', (('value', 'equity'),)))): {
                 'signal': (('side', (('value', -1),)), ('quantity', 1), ('price', None))},
             ('2021-01-03T00:00:00', (('ticker', 'MSFT'), ('security_type', (('value', 'equity'),)))): {
                 'signal': (('side', (('value', -1),)), ('quantity', 1), ('price', None))}}
        )

    def test_set_position(self):
        position = dx.Inventory({security: 100 for security in self.security_manager.values()})

        position_params = {
            "obj": position.to_dict(serializable=True)
        }

        response = requests.post("http://localhost:8000/position", json.dumps(position_params))
        status = response.json()["status"]

        self.assertEqual(
            status,
            "success"
        )

    def test_get_position(self):
        response = requests.get("http://localhost:8000/position")

        data = response.json()["data"]

        position = dx.Inventory.from_dict(serialized=True, **data).map_securities(self.security_manager)

        self.assertEqual(
            position,
            self.executor.position
        )


if __name__ == '__main__':
    unittest.main()
