import unittest

import pandas as pd

import dxlib as dx


class TestHistory(unittest.TestCase):
    def setUp(self):
        self.schema = dx.Schema(
            levels=[dx.SchemaLevel.DATE, dx.SchemaLevel.SECURITY],
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

    def test_apply(self):
        history = dx.History(self.sample_data, self.schema)
        history = history.apply({dx.SchemaLevel.SECURITY: lambda x: x + 1})

        self.assertEqual(history.df.loc[history.df.index[0], "close"], 101)

    def test_apply_other(self):
        history = dx.History(self.sample_data, self.schema)
        other = dx.History(self.sample_data, self.schema)

        history = history.apply_on(other, lambda x, y: x + y)

        self.assertEqual(history.df.loc[history.df.index[0], "close"], 200)

    def test_integration(self):
        history = dx.History(self.sample_data, self.schema)

        prices = history.apply({dx.SchemaLevel.SECURITY: lambda x: x + 1})
        shares = history.apply({dx.SchemaLevel.SECURITY: lambda x: x / 100})

        daily_returns = prices.apply({dx.SchemaLevel.SECURITY: lambda x: x.pct_change().shift(-1).fillna(0)})
        portfolio_returns = shares.apply_on(
            daily_returns,
            lambda x, y: pd.DataFrame(x.values * y.values, index=x.index, columns=["returns"])
        )

        df = portfolio_returns.df

        self.assertEqual(df.shape, (4, 1))
        self.assertEqual(df.index.names, ["date", "security"])
        self.assertEqual(df.columns, ["returns"])

        # (111 - 101) / 101 * 1 = 0.09901
        # (211 - 201) / 201 * 2 = 0.09950
        self.assertAlmostEqual(df.loc[df.index[0], "returns"], 0.09901, 5)
        self.assertAlmostEqual(df.loc[df.index[1], "returns"], 0.09950, 5)


if __name__ == "__main__":
    unittest.main()
