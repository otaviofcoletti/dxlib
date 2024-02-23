import unittest

import pandas as pd

import dxlib as dx


class TestHistory(unittest.TestCase):
    def setUp(self):
        self.scheme = dx.HistorySchema(
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
        history = dx.History(df, self.scheme)

        self.assertEqual(history.df.shape, (4, 1))
        self.assertEqual(history.df.index.names, ["date", "security"])
        self.assertEqual(history.df.columns, ["close"])

    def test_create_from_dict(self):
        history = dx.History(self.sample_data, self.scheme)

        self.assertEqual(history.df.shape, (4, 1))
        self.assertEqual(history.df.index.names, ["date", "security"])
        self.assertEqual(history.df.columns, ["close"])

    def test_get_df(self):
        history = dx.History(self.sample_data, self.scheme)
        df = history.get_df()

        self.assertEqual(df.shape, (4, 1))
        self.assertEqual(df.index.names, ["date", "security"])
        self.assertEqual(df.columns, ["close"])

    def test_add_tuple(self):
        history = dx.History(scheme=self.scheme)
        history.add(((pd.Timestamp("2021-01-01"), "AAPL"), {"close": 100}))

        self.assertEqual(history.df.shape, (1, 1))
        self.assertEqual(history.df.index.names, ["date", "security"])
        self.assertEqual(history.df.columns, ["close"])

        # test if security ticker is aapl
        self.assertEqual(history.df.index[0][1].ticker, "AAPL")

    def test_add_external(self):
        external_security = dx.Security("TSLA")
        history = dx.History(scheme=self.scheme)
        self.scheme.security_manager += external_security

        history.add(((pd.Timestamp("2021-01-01"), "TSLA"), {"close": 100}))

        self.assertEqual(history.df.shape, (1, 1))
        self.assertEqual(history.df.index.names, ["date", "security"])
        self.assertEqual(history.df.columns, ["close"])

    def test_to_dict(self):
        history = dx.History(self.sample_data, self.scheme)
        history_dict = history.to_dict()
        """
        history_dict = {
            ('2021-01-01T00:00:00', (('ticker', 'AAPL'), ('security_type', (('value', 'equity'),)))): {'close': 100},
            ('2021-01-01T00:00:00', (('ticker', 'MSFT'), ('security_type', (('value', 'equity'),)))): {'close': 200},
            ('2021-01-02T00:00:00', (('ticker', 'AAPL'), ('security_type', (('value', 'equity'),)))): {'close': 110},
            ('2021-01-02T00:00:00', (('ticker', 'MSFT'), ('security_type', (('value', 'equity'),)))): {'close': 210}
        }
        """

        df = history_dict["df"]

        self.assertEqual(len(df), 4)
        self.assertEqual(
            df[('2021-01-01T00:00:00', (('ticker', 'AAPL'), ('security_type', (('value', 'equity'),))))],
            {"close": 100},
        )

        self.assertEqual(
            df[('2021-01-01T00:00:00', (('ticker', 'MSFT'), ('security_type', (('value', 'equity'),))))],
            {"close": 200},
        )


if __name__ == "__main__":
    unittest.main()
