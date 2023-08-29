# """
# Retorno de uma Carteira com Python e Backtesting (BT)
#
# Authors: Rafael Zimmer
# """
# import pandas as pd
# import numpy as np
# import matplotlib.pyplot as plt
#
# import yfinance as yf
# import bt
#
# import pmdarima as pm
# from pmdarima.arima import ndiffs
# import warnings
#
#
# class Portfolio:
#     def __init__(self, tickers=None):
#         if tickers is None:
#             tickers = ["PETR4.SA", "TOTS3.SA"]
#         start_date = "2020-01-01"
#         end_date = "2022-12-31"
#
#         portfolio = yf.download(tickers, start=start_date, end=end_date)["Adj Close"]
#
#         self.stocks = portfolio.fillna(method="ffill")
#         self.total_stocks = len(self.stocks.columns)
#         self.index = self.stocks.sum(axis=1)
#
#
# class Strategy:
#     def __init__(self, strategy, name):
#         if strategy == "rebalance":
#             self.strategy = bt.Strategy(
#                 name,
#                 [
#                     bt.algos.RunMonthly(run_on_end_of_period=True),
#                     bt.algos.SelectAll(),
#                     bt.algos.WeighEqually(),
#                     bt.algos.Rebalance(),
#                 ],
#             )
#         elif strategy == "buy&hold":
#             self.strategy = bt.Strategy(
#                 name,
#                 [
#                     bt.algos.RunOnce(),
#                     bt.algos.SelectAll(),
#                     bt.algos.WeighEqually(),
#                     bt.algos.Rebalance(),
#                 ],
#             )
#         else:
#             self.strategy = None
#
#     def run(self, portfolio):
#         backtest = bt.Backtest(self.strategy, portfolio)
#         return bt.run(backtest)
#
#
# class Position:
#     def __init__(self, portfolio, weights=None, total=None, shares=None):
#         if shares is not None:
#             self.shares = shares
#             self.portfolio = portfolio
#         else:
#             if weights is None:
#                 weights = [1 / portfolio.total_stocks] * portfolio.total_stocks
#             if total is None:
#                 total = portfolio.index.iloc[0]
#             starting_shares = total * (1 / portfolio.stocks.iloc[0] * weights)
#
#             self.portfolio = portfolio
#             self.shares = portfolio.stocks.apply(lambda _: starting_shares, axis=1)
#
#     def get_weights(self, idx=None):
#         if idx is None:
#             return self.shares.apply(lambda col: col / sum(col), axis=1)
#         else:
#             total_value = sum(self.shares.iloc[idx] * self.portfolio.stocks.iloc[idx])
#             return self.shares.iloc[idx] / total_value
#
#     def get_value(self, idx=None):
#         if idx is None:
#             return (self.shares * self.portfolio.stocks).sum(axis=1)
#         else:
#             return (self.shares.iloc[idx] * self.portfolio.stocks[idx]).sum(axis=1)
#
#     def operate_shares(self, new_shares, idx, inplace=True):
#         if inplace:
#             new_position = self.shares
#         else:
#             new_position = self.shares.copy()
#
#         if (new_position.iloc[idx] + new_shares > 0).all():
#             new_position.iloc[idx:] += new_shares
#         else:
#             raise ValueError("Can't have negative position.")
#         return new_position
#
#     def operate_weights(self, weight_change, idx, inplace=True):
#         if sum(weight_change) != 1:
#             raise ValueError("Weight change must sum up to 0.")
#
#         if inplace:
#             new_position = self.shares
#         else:
#             new_position = self.shares.copy()
#
#         new_shares = (
#             sum(self.shares.iloc[idx] * self.portfolio.stocks.iloc[idx])
#             / self.portfolio.stocks.iloc[idx]
#         )
#         new_shares *= weight_change
#
#         if (new_position.iloc[idx] + new_shares > 0).all():
#             new_position.iloc[idx:] += new_shares
#         else:
#             raise ValueError("Can't have negative position")
#         return new_position
#
#     def changes(self):
#         return pd.DataFrame(
#             [
#                 1 - self.portfolio.stocks.iloc[i] / self.portfolio.stocks.iloc[i - 1]
#                 if i >= 1
#                 else [0] * len(self.portfolio.stocks.columns)
#                 for i in range(len(self.portfolio.stocks))
#             ],
#             index=self.portfolio.stocks.index,
#             columns=self.portfolio.stocks.columns,
#         )
#
#     def cumulative_changes(self):
#         portfolio_changes = self.changes()
#
#         return pd.DataFrame(
#             [
#                 portfolio_changes.iloc[i] + portfolio_changes.iloc[i - 1]
#                 if i >= 1
#                 else [0] * len(self.portfolio.stocks.columns)
#                 for i in range(len(self.portfolio.stocks))
#             ],
#             index=self.portfolio.stocks.index,
#             columns=self.portfolio.stocks.columns,
#         )
#
#
# class ForecastRebalance(Strategy):
#     def __init__(self, name, portfolio, prediction_window=5):
#         super().__init__("", name)
#         self.portfolio = portfolio
#
#         self.prediction_window = prediction_window
#         self.model = None
#         self.position = None
#
#     def train(self, stock):
#         size = len(stock)
#         split_size = size // 10
#
#         build_set = stock[split_size:]
#
#         kpss_diffs = ndiffs(build_set, alpha=0.05, test="kpss", max_d=6)
#         adf_diffs = ndiffs(build_set, alpha=0.05, test="adf", max_d=6)
#         n_diffs = max(adf_diffs, kpss_diffs)
#
#         model = pm.auto_arima(
#             build_set,
#             d=n_diffs,
#             seasonal=False,
#             stepwise=True,
#             suppress_warnings=True,
#             error_action="ignore",
#             max_p=6,
#             maxiter=40,
#             max_order=None,
#             trace=True,
#         )
#         return model
#
#     def predict(self, model):
#         return model.predict(n_periods=self.prediction_window, return_conf_int=True)
#
#     def run(self, weights=None, total=10e3):
#         models = {
#             ticker: self.train(self.portfolio.stocks[ticker])
#             for ticker in self.portfolio.stocks.columns
#         }
#         position = Position(self.portfolio, weights=weights, total=total)
#
#         for interval in range(
#             len(self.portfolio.stocks) // 10, len(self.portfolio.stocks), 5
#         ):
#             with warnings.catch_warnings():
#                 warnings.simplefilter("ignore")
#                 forecasts = pd.DataFrame(
#                     {
#                         ticker: np.array(self.predict(models[ticker])[0])
#                         for ticker in self.portfolio.stocks.columns
#                     }
#                 )
#
#             prices = self.portfolio.stocks.iloc[
#                 interval : min(interval + 5, len(self.portfolio.stocks))
#             ]
#
#             change_forecast = (forecasts.iloc[-1] - forecasts.iloc[0]) / forecasts.iloc[
#                 0
#             ]
#             change_real = (prices.iloc[-1] - prices.iloc[0]) / prices.iloc[0]
#
#             list(
#                 map(
#                     lambda ticker: models[ticker].update(prices[ticker]),
#                     self.portfolio.stocks.columns,
#                 )
#             )
#
#             print("Change: ", change_forecast)
#             print("Error: ", abs(change_forecast - change_real), end="\n\n")
#
#         self.position = position
#
#
# def test_position(portfolio, starting_cash=10e3):
#     position = Position(portfolio, total=starting_cash)
#     position_value = position.get_value()
#
#     print("Position value over time: ")
#     print(position_value)
#     print(
#         "Starting value: {:.2f}, final value: {:.2f}".format(
#             starting_cash, position_value.iloc[-1], end="\n\n"
#         )
#     )
#
#     # Compra de R$ 1000 em PETR4 7 dias atrás
#     new_shares = [1000 / portfolio.stocks.iloc[-7, 0], 0]
#     dt7 = position.operate_shares(new_shares, idx=-7, inplace=False)
#
#     # Compra de R$ 1000 em PETR4 2 dias atrás
#     new_shares = [1000 / portfolio.stocks.iloc[-2, 0], 0]
#     dt2 = position.operate_shares(new_shares, idx=-2, inplace=False)
#
#     print(
#         "Perda devido à dinheiro parado: R$ {:.2f}".format(
#             sum((dt2.iloc[-1] - dt7.iloc[-1]) * portfolio.stocks.iloc[-1])
#         )
#     )
#
#
# def main():
#     starting_cash = 10e3
#     portfolio = Portfolio()
#
#     strategy = ForecastRebalance(name="Forecast&Rebalance", portfolio=portfolio)
#     strategy.run()
#     plt.plot(strategy.position.get_value())
#     plt.show()
#
#
# if __name__ == "__main__":
#     main()
