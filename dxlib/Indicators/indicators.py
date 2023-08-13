import pandas as pd

class Indicators():
  def __init__(self, history, window=252):
    self.history = history
    self.window = window

  def sharpe_ratio(self, risk_free=0.1):
    log_returns = np.log(self.history.pct_change(periods=self.window)).dropna()
    
    volatility = log_returns.rolling(window=self.window).std()*np.sqrt(self.window)
    
    sharpe_ratio = (log_returns.rolling(window=self.window).mean() - risk_free)*self.window / volatility
    
    return sharpe_ratio

  def rsi(self):

    delta = self.history.iloc[-self.window-1:].diff() 
    delta.dropna(inplace=True)

    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)

    # Calculate the average gain and average loss for the specified period
    avg_gain = gain.mean()
    avg_loss = loss.mean()

    # Calculate the Relative Strength (RS) by dividing the average gain by the average loss
    rs = avg_gain / avg_loss

    # Calculate the Relative Strength Index (RSI)
    RSI = 100 - (100 / (1 + rs))

    return RSI
