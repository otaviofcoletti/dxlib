import json
import time
import unittest

import pandas as pd
import requests

import dxlib as dx
from dxlib.interfaces.internal.executor_interface import ExecutorHTTPInterface
from dxlib.strategies.custom_strategies import RsiStrategy


class TestExecutorInterface(unittest.TestCase):
    def setUp(self):
        self.strategy = RsiStrategy(window=1)

        self.security_manager = dx.SecurityManager.from_list(["AAPL", "MSFT"])
        self.schema = dx.HistorySchema(
            levels=[dx.HistoryLevel.DATE, dx.HistoryLevel.SECURITY],
            fields=["close"],
            security_manager=self.security_manager,
        )

        self.inventory = dx.Inventory({security: 0 for security in self.security_manager.values()})
        self.executor = dx.Executor(self.strategy, self.inventory, self.schema)

        self.interface = ExecutorHTTPInterface(self.executor)
        self.server = dx.HTTPServer(port=8000)

        self.server.add_interface(self.interface)

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
            "obj": history.to_dict(serialize=True),
            "in_place": False
        }

        self.server.start()
        while not self.server.alive:
            time.sleep(0.1)

        response = requests.post("http://localhost:8000/run", json.dumps(run_params))
        print(response)

        self.server.stop()


if __name__ == '__main__':
    unittest.main()
