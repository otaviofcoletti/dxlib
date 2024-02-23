import json
import time
import unittest

import pandas as pd
import requests

import dxlib as dx
from dxlib.core.components.history import SignalSchema
from dxlib.interfaces.internal.executor_interface import ExecutorHTTPInterface
from dxlib.strategies.custom_strategies import RsiStrategy


class TestExecutorInterface(unittest.TestCase):
    def setUp(self):
        self.strategy = RsiStrategy(window=1)

        self.security_manager = dx.SecurityManager.from_list(["AAPL", "MSFT"])
        self.scheme = dx.HistorySchema(
            levels=[dx.HistoryLevel.DATE, dx.HistoryLevel.SECURITY],
            fields=["close"],
            security_manager=self.security_manager,
        )

        self.inventory = dx.Inventory({security: 0 for security in self.security_manager.values()})
        self.executor = dx.Executor(self.strategy, self.inventory, self.scheme)

        self.interface = ExecutorHTTPInterface(self.executor)

    def test_run(self):
        server = dx.HTTPServer(port=8000)
        server.add_interface(self.interface)
        server.start()

        history = dx.History(
            {
                (pd.Timestamp("2021-01-01"), "AAPL"): {"close": 100},
                (pd.Timestamp("2021-01-01"), "MSFT"): {"close": 200},
                (pd.Timestamp("2021-01-02"), "AAPL"): {"close": 110},
                (pd.Timestamp("2021-01-02"), "MSFT"): {"close": 210},
                (pd.Timestamp("2021-01-03"), "AAPL"): {"close": 120},
                (pd.Timestamp("2021-01-03"), "MSFT"): {"close": 220},
            },
            self.scheme,
        )

        run_params = {
            "obj": history.to_dict(serializable=True),
            "in_place": False
        }

        while not server.alive:
            time.sleep(0.1)

        response = requests.post("http://localhost:8000/run", json.dumps(run_params))

        data = response.json()["data"]

        signal_scheme = SignalSchema(security_manager=self.security_manager)
        signal_history = dx.History.from_dict(signal_scheme, serialized=True, **data)

        self.assertEqual(
            signal_history.to_dict(),
            {'df': {
                ('2021-01-01T00:00:00', (('ticker', 'AAPL'), ('security_type', (('value', 'equity'),)))): {
                    'signal': (('side', (('value', 0),)), ('quantity', None), ('price', None))},
                ('2021-01-01T00:00:00', (('ticker', 'MSFT'), ('security_type', (('value', 'equity'),)))): {
                    'signal': (('side', (('value', 0),)), ('quantity', None), ('price', None))},
                ('2021-01-02T00:00:00', (('ticker', 'AAPL'), ('security_type', (('value', 'equity'),)))): {
                    'signal': (('side', (('value', 0),)), ('quantity', None), ('price', None))},
                ('2021-01-02T00:00:00', (('ticker', 'MSFT'), ('security_type', (('value', 'equity'),)))): {
                    'signal': (('side', (('value', 0),)), ('quantity', None), ('price', None))},
                ('2021-01-03T00:00:00', (('ticker', 'AAPL'), ('security_type', (('value', 'equity'),)))): {
                    'signal': (('side', (('value', 0),)), ('quantity', None), ('price', None))},
                ('2021-01-03T00:00:00', (('ticker', 'MSFT'), ('security_type', (('value', 'equity'),)))): {
                    'signal': (('side', (('value', 0),)), ('quantity', None), ('price', None))}
            }}
        )

        server.stop()

    def test_set_position(self):
        server = dx.HTTPServer(port=8001)
        server.add_interface(self.interface)
        server.start()

        position = dx.Inventory({security: 100 for security in self.security_manager.values()})

        position_params = {
            "obj": position.to_dict(serializable=True)
        }

        while not server.alive:
            time.sleep(0.1)

        response = requests.post("http://localhost:8001/position", json.dumps(position_params))
        status = response.json()["status"]

        self.assertEqual(
            status,
            "success"
        )

        server.stop()

    def test_get_position(self):
        server = dx.HTTPServer(port=8002)
        server.add_interface(self.interface)
        server.start()

        while not server.alive:
            time.sleep(0.1)

        response = requests.get("http://localhost:8002/position")

        data = response.json()["data"]

        position = dx.Inventory.from_dict(serialized=True, **data).map_securities(self.security_manager)

        self.assertEqual(
            position,
            self.executor.position
        )

        server.stop()


if __name__ == '__main__':
    unittest.main()
