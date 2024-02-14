import unittest

import pandas as pd
import dxlib as dx


class TestHistory(unittest.TestCase):
    def setUp(self):
        self.schema = dx.HistorySchema(
            levels=[dx.HistoryLevel.DATE, dx.HistoryLevel.SECURITY],
            fields=["close"],
            security_manager=dx.SecurityManager.from_list(["AAPL", "MSFT"]),
        )
        self.sample_data = {
            (pd.Timestamp("2021-01-01"), "AAPL"): {"close": 100},
            (pd.Timestamp("2021-01-01"), "MSFT"): {"close": 200},
            (pd.Timestamp("2021-01-02"), "AAPL"): {"close": 110},
            (pd.Timestamp("2021-01-02"), "MSFT"): {"close": 210},
        }

    def test_create_from_df(self):
        df = pd.DataFrame.from_dict(self.sample_data, orient="index")
        history = dx.History(df, self.schema)

        self.assertEqual(history.df.shape, (4, 1))
        self.assertEqual(history.df.index.names, ["date", "security"])
        self.assertEqual(history.df.columns, ["close"])

    def test_create_from_dict(self):
        history = dx.History(self.sample_data, self.schema)

        self.assertEqual(history.df.shape, (4, 1))
        self.assertEqual(history.df.index.names, ["date", "security"])
        self.assertEqual(history.df.columns, ["close"])

    def test_get_df(self):
        history = dx.History(self.sample_data, self.schema)
        df = history.get_df()

        self.assertEqual(df.shape, (4, 1))
        self.assertEqual(df.index.names, ["date", "security"])
        self.assertEqual(df.columns, ["close"])

    def test_add_tuple(self):
        history = dx.History(schema=self.schema)
        history.add(((pd.Timestamp("2021-01-01"), "AAPL"), {"close": 100}))

        self.assertEqual(history.df.shape, (1, 1))
        self.assertEqual(history.df.index.names, ["date", "security"])
        self.assertEqual(history.df.columns, ["close"])

        # test if security ticker is aapl
        self.assertEqual(history.df.index[0][1].ticker, "AAPL")

        print(history.df)

    def test_add_external(self):
        external_security = dx.Security("TSLA")
        history = dx.History(schema=self.schema)
        self.schema.security_manager += external_security

        history.add(((pd.Timestamp("2021-01-01"), "TSLA"), {"close": 100}))

        self.assertEqual(history.df.shape, (1, 1))
        self.assertEqual(history.df.index.names, ["date", "security"])
        self.assertEqual(history.df.columns, ["close"])

    def test_to_dict(self):
        history = dx.History(self.sample_data, self.schema)
        history_dict = history.to_dict()
        # {'df': {('2021-01-01T00:00:00', (('ticker', 'AAPL'), ('security_type', (('name', 'equity'),)))): {'close': 100}, ('2021-01-01T00:00:00', (('ticker', 'MSFT'), ('security_type', (('name', 'equity'),)))): {'close': 200}, ('2021-01-02T00:00:00', (('ticker', 'AAPL'), ('security_type', (('name', 'equity'),)))): {'close': 110}, ('2021-01-02T00:00:00', (('ticker', 'MSFT'), ('security_type', (('name', 'equity'),)))): {'close': 210}}, 'schema': {'levels': [{'name': 'DATE'}, {'name': 'SECURITY'}], 'fields': ['close'], 'security_manager': {'securities': {'AAPL': {'ticker': 'AAPL', 'security_type': {'name': 'equity'}}, 'MSFT': {'ticker': 'MSFT', 'security_type': {'name': 'equity'}}}, 'cash': {'ticker': 'cash', 'security_type': {'name': 'cash'}}}}}

        self.assertEqual(history_dict["schema"]["levels"], [{'name': 'DATE'}, {'name': 'SECURITY'}])
        self.assertEqual(history_dict["schema"]["fields"], ["close"])

        self.assertEqual(
            history_dict["schema"]["security_manager"]["securities"]["AAPL"]["ticker"],
            "AAPL",
        )
        self.assertEqual(
            history_dict["schema"]["security_manager"]["securities"]["MSFT"]["ticker"],
            "MSFT",
        )


if __name__ == "__main__":
    unittest.main()
