import pandas as pd
import numpy as np
from rich import print
from rich.logging import RichHandler
import logging


class Portfolio:
    def __init__(self, symbols, initial_cash=100000):
        self.symbols = symbols
        self.portfolio = pd.DataFrame(columns=symbols + ['Cash'])
        self.portfolio.loc[0, self.symbols] = 0
        self.portfolio.loc[0, 'Cash'] = initial_cash
        self.transaction_history = []

        self.logger = logging.getLogger("Portfolio")
        self.logger.setLevel(logging.INFO)
        self.logger.addHandler(RichHandler())

    def buy_stock(self, symbol, quantity, price):
        cost = quantity * price
        if cost > self.portfolio['Cash'].iloc[-1]:
            raise ValueError("Not enough cash to execute the order.")
        self.portfolio[symbol].iloc[-1] += quantity
        self.portfolio['Cash'].iloc[-1] -= cost
        self.record_transaction(symbol, "Buy", quantity, price)

    def sell_stock(self, symbol, quantity, price):
        if self.portfolio[symbol].iloc[-1] < quantity:
            raise ValueError("Not enough stocks to execute the order.")
        revenue = quantity * price
        self.portfolio[symbol].iloc[-1] -= quantity
        self.portfolio['Cash'].iloc[-1] += revenue
        self.record_transaction(symbol, "Sell", quantity, price)

    def record_transaction(self, symbol, action, quantity, price):
        transaction = {
            'Symbol': symbol,
            'Action': action,
            'Quantity': quantity,
            'Price': price
        }
        self.transaction_history.append(transaction)
        self.logger.info(f"Transaction recorded: {action} {quantity} {symbol} @ ${price:.2f}")

    def get_portfolio_value(self, prices):
        stock_value = (self.portfolio[self.symbols] * prices).sum(axis=1)
        cash_value = self.portfolio['Cash']
        total_value = stock_value + cash_value
        return total_value

    def calculate_returns(self):
        total_value = self.get_portfolio_value(self.portfolio[self.symbols])
        returns = total_value.pct_change()
        return returns

    def calculate_max_drawdown(self):
        total_value = self.get_portfolio_value(self.portfolio[self.symbols])
        cumulative_returns = (1 + total_value.pct_change()).cumprod()
        peak = cumulative_returns.expanding(min_periods=1).max()
        drawdown = (cumulative_returns - peak) / peak
        max_drawdown = drawdown.min()
        return max_drawdown

    def print_portfolio_summary(self):
        print("\nPortfolio Summary:")
        print(self.portfolio)
        print("\nTransaction History:")
        df = pd.DataFrame(self.transaction_history)
        print(df)


# Example usage:
if __name__ == "__main__":
    symbols = ['AAPL', 'GOOGL', 'MSFT']
    price_data = np.array([
        [150.0, 2500.0, 300.0],
        [152.0, 2550.0, 305.0],
        [151.5, 2510.0, 302.0],
        [155.0, 2555.0, 308.0],
        [157.0, 2540.0, 306.0],
    ])

    portfolio = Portfolio(symbols)

    for i, prices in enumerate(price_data):
        if i > 0:
            portfolio.portfolio.loc[i] = portfolio.portfolio.loc[i - 1]
        portfolio.portfolio.loc[i, symbols] = prices

        if i > 0 and i < 4:
            portfolio.buy_stock('GOOGL', 2, portfolio.portfolio.loc[i, 'GOOGL'])
        elif i == 4:
            portfolio.sell_stock('MSFT', 50, portfolio.portfolio.loc[i, 'MSFT'])

    returns = portfolio.calculate_returns()
    max_drawdown = portfolio.calculate_max_drawdown()

    portfolio.print_portfolio_summary()
    print("\nReturns:")
    print(returns)
    print("Max Drawdown:", max_drawdown)
