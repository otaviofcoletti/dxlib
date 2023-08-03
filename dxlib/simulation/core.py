import numpy as np
from portfolio import Portfolio
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
import seaborn


class Simulation:
    def __init__(self, portfolio, price_data):
        self.portfolio = portfolio
        self.price_data = price_data

    def momentum(self, security, T):
        momentum_T = security.copy()
        momentum_T[0:T] = 0

        for i in range(T, len(momentum_T.values)):
            momentum_T.iloc[i] = security.iloc[i] / security.iloc[i - T]

        return momentum_T

    def price_size(self, security, T):
        pcs = security / security.rolling(T).sum()

        return pcs.fillna(method='bfill')

    def vol_rolling(self, security, T):
        vol = security.pct_change().rolling(T).std(ddof=0)

        return vol.fillna(method='bfill')

    def train_test_split(self, features, labels, percentage):
        size = int(len(features) * percentage)

        train = {"x": features[10:size], "y": labels[10:size].flatten()}
        test = {"x": features[size:], "y": labels[size:].flatten()}

        return train, test

    def simulate_trade_allocation(self, title, y_pred, basis):
        y_pred_portfolio = np.array([1 - y_pred, y_pred]).T
        basis['BUY-PRED'] = np.argmin(y_pred_portfolio, axis=1)
        basis['SELL-PRED'] = np.argmax(y_pred_portfolio, axis=1)

        basis['BUY-PRED'] = basis['BUY-PRED'].shift(1).fillna(1)
        basis['SELL-PRED'] = basis['SELL-PRED'].shift(1).fillna(0)

        basis['PRED-PERCENTAGE'] = basis['PETR4.SA'].to_numpy().flatten() * basis['BUY-PRED'].to_numpy() + \
                                   basis['AGRO3.SAO'].to_numpy().flatten() * basis['SELL-PRED'].to_numpy()
        basis['PRED-CHANGES'] = (1 + basis['PRED-PERCENTAGE'].fillna(0).to_numpy()).cumprod()

        print(title)
        seaborn.lineplot(100 * basis[['PRED-CHANGES', "PETR4.SA", "AGRO3.SAO"]])
        return basis["PRED-CHANGES"], \
            (basis["PRED-CHANGES"].iloc[-1] - basis["PRED-CHANGES"].iloc[0]) / basis["PRED-CHANGES"].iloc[0]

    def run(self, operations=None):
        for i, prices in enumerate(self.price_data):
            if i > 0:
                self.portfolio.portfolio.loc[i] = self.portfolio.portfolio.loc[i - 1]
            self.portfolio.portfolio.loc[i, self.portfolio.symbols] = prices

            if operations is not None:
                for operation in operations:
                    operation.execute(self.portfolio, i)

        returns = self.portfolio.calculate_returns()
        max_drawdown = self.portfolio.calculate_max_drawdown()

        self.portfolio.print_portfolio_summary()
        print("\nReturns:")
        print(returns)
        print("Max Drawdown:", max_drawdown)

        basis = self.portfolio.portfolio[self.portfolio.symbols].copy()
        basis = basis.pct_change()
        basis['1T'] = self.momentum(basis['PETR4.SA'], 30)
        basis['3T'] = self.momentum(basis['PETR4.SA'], 90)
        basis['6T'] = self.momentum(basis['PETR4.SA'], 180)

        basis["BUY"] = np.argmin(basis[self.portfolio.symbols].to_numpy(), axis=1)

        features = basis[["1T", "3T", "6T"]].to_numpy()
        labels = basis[["BUY"]].to_numpy()

        train, test = self.train_test_split(features, labels, 0.5)

        clf = RandomForestClassifier()
        clf.fit(train["x"], train["y"])

        y_pred_train = clf.predict(train["x"])
        y_pred_val = clf.predict(test["x"])
        y_pred = clf.predict(features)

        pred_changes, returns = self.simulate_trade_allocation("RandomForest for 1, 3 and 6 months Momentum class",
                                                               y_pred, basis)
        print(pred_changes, f"\nReturns: {returns}")
        print("Accuracy train:", accuracy_score(train["y"], y_pred_train))
        print("Accuracy validation:", accuracy_score(test["y"], y_pred_val))


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
    simulation = Simulation(portfolio, price_data)

    class BuyOnCondition:
        def __init__(self):
            pass

        def execute(self, portfolio, current_day):
            if current_day > 0 and current_day < 4:
                portfolio.buy_stock('GOOGL', 2, portfolio.portfolio.loc[current_day, 'GOOGL'])
            elif current_day == 4:
                portfolio.sell_stock('MSFT', 50, portfolio.portfolio.loc[current_day, 'MSFT'])


    operations = [BuyOnCondition()]
    simulation.run(operations)
