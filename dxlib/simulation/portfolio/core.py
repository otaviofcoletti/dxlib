import numpy as np
import pandas as pd


class PortfolioSimulator:
    def __init__(self, initial_cash, symbols):
        self.initial_cash = initial_cash
        self.symbols = symbols
        self.portfolio = pd.DataFrame(columns=symbols + ['Cash'])
        self.portfolio.loc[0, self.symbols] = 0
        self.portfolio.loc[0, 'Cash'] = initial_cash
        self.current_day = 0  # Initialize current_day attribute

    def buy_stock(self, symbol, quantity, price):
        cost = quantity * price
        if cost > self.portfolio.loc[self.current_day, 'Cash']:
            raise ValueError("Not enough cash to execute the order.")
        self.portfolio.loc[self.current_day, symbol] += quantity
        self.portfolio.loc[self.current_day, 'Cash'] -= cost

    def update_portfolio_prices(self, prices):
        self.portfolio.loc[self.current_day, self.symbols] = prices

    def get_current_weight(self):
        total_value = self.portfolio.loc[self.current_day, self.symbols].dot(
            self.portfolio.loc[self.current_day, self.symbols]
        )
        weights = self.portfolio.loc[self.current_day, self.symbols] / total_value
        return weights

    def run_simulation(self, price_data):
        for i, prices in enumerate(price_data):
            if i == 0:
                continue
            self.current_day = i
            self.update_portfolio_prices(prices)
            self.portfolio.loc[i] = self.portfolio.loc[i - 1]

        return self.portfolio

    def calculate_returns(self):
        portfolio_value = (self.portfolio[self.symbols] * self.portfolio[self.symbols].shift(-1)).sum(axis=1)
        portfolio_returns = portfolio_value.pct_change()
        return portfolio_returns


# Example usage:
if __name__ == "__main__":
    symbols = ['AAPL', 'GOOGL', 'MSFT']  # List of stock symbols
    initial_cash = 100000  # Initial cash balance

    # Example price_data for 5 days (3 stocks, 5 days)
    price_data = np.array([
        [150.0, 2500.0, 300.0],
        [152.0, 2550.0, 305.0],
        [151.5, 2510.0, 302.0],
        [155.0, 2555.0, 308.0],
        [157.0, 2540.0, 306.0],
    ])

    # Create the PortfolioSimulator instance
    portfolio_simulator = PortfolioSimulator(initial_cash, symbols)

    # Simulate buying stocks
    portfolio_simulator.buy_stock('AAPL', 50, price_data[0, 0])
    portfolio_simulator.buy_stock('GOOGL', 5, price_data[0, 1])
    portfolio_simulator.buy_stock('MSFT', 100, price_data[0, 2])

    # Run the simulation and calculate returns
    portfolio = portfolio_simulator.run_simulation(price_data)
    returns = portfolio_simulator.calculate_returns()

    print(portfolio)
    print("Returns:")
    print(returns)
