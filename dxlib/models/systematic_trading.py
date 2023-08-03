# if i > 0:
#     self.portfolio.history.df.loc[i] = self.portfolio.history.df.loc[i - 1]
# self.portfolio.history.df.loc[i, self.portfolio.history.df.columns] = prices

#     if operations is not None:
#         for operation in operations:
#             operation.execute(self.portfolio, i)
#
# returns = self.portfolio.calculate_returns()
# max_drawdown = self.portfolio.calculate_max_drawdown()
#
# self.portfolio.print_portfolio_summary()
# print("\nReturns:")
# print(returns)
# print("Max Drawdown:", max_drawdown)
#
# basis = self.portfolio.portfolio[self.portfolio.symbols].copy()
# basis = basis.pct_change()
# basis['1T'] = self.momentum(basis[symbol], 30)
# basis['3T'] = self.momentum(basis[symbol], 90)
# basis['6T'] = self.momentum(basis[symbol], 180)
#
# basis["BUY"] = np.argmin(basis[self.portfolio.symbols].to_numpy(), axis=1)
#
# features = basis[["1T", "3T", "6T"]].to_numpy()
# labels = basis[["BUY"]].to_numpy()
#
# train, test = self.train_test_split(features, labels, 0.5)
#
# clf = RandomForestClassifier()
# clf.fit(train["x"], train["y"])
#
# y_pred_train = clf.predict(train["x"])
# y_pred_val = clf.predict(test["x"])
# y_pred = clf.predict(features)
#
# pred_changes, returns = self.simulate_trade_allocation("RandomForest for 1, 3 and 6 months Momentum class",
#                                                        y_pred, basis, symbol, symbol2)
# print(pred_changes, f"\nReturns: {returns}")
# print("Accuracy train:", accuracy_score(train["y"], y_pred_train))
# print("Accuracy validation:", accuracy_score(test["y"], y_pred_val))