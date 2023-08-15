# Quantitative Analysis Library (dxlib)

`dxlib` offers a rich set of tools tailored for traders, researchers, and quantitative analysts, covering everything from basic statistical methods to comprehensive trading simulations. It emphasizes a unified interface for fetching and analyzing data, ensuring consistent and predictable outputs irrespective of data sources.

## Installation

Use the package manager [pip](https://pip.pypa.io/) to install dxlib.

```bash
pip install dxlib
```

## Modules Overview

### Research Module

```python
from dxlib import finite_differences
import numpy as np
import matplotlib.pyplot as plt

x = np.arange(-3, 3, 0.1)
y = np.tanh(x)
dy = finite_differences(x, y)
plt.plot(x, dy)
plt.show()
```

### Simulation Module

Harness `dxlib` to simulate trading strategies:

```python
import dxlib as dx
from dxlib.simulation import SimulationManager

data = dx.api.YFinanceAPI().get_historical_bars(["AAPL", "MSFT", "GOOGL", "AMZN"], start="2022-01-01", end="2022-12-31")
portfolio = dx.Portfolio().add_cash(1e4)
strategy = dx.strategies.RsiStrategy()
simulation_manager = SimulationManager(portfolio, strategy, data["Close"])
```

**Highlight: Built-in Server**

The simulation manager features an embedded server that serves requests related to the simulation process. This allows for real-time monitoring and potential interaction with running simulations. Check out the `Server` class in the `simulation` module for more details.

Start the server with `simulation_manager.start_server()`. Check the logs for server activity and exception handling.

```python

import dxlib as dx
from dxlib.simulation import SimulationManager

data = dx.api.YFinanceAPI().get_historical_bars(["AAPL", "MSFT", "GOOGL", "AMZN"], start="2022-01-01", end="2022-12-31")
portfolio = dx.Portfolio().add_cash(1e4)
strategy = dx.strategies.RsiStrategy()

logger = dx.info_logger("simulation_manager")
simulation_manager = SimulationManager(portfolio, strategy, data["Close"], use_server=True, port=5000, logger=logger)

simulation_manager.start_server()

try:
    while simulation_manager.server.is_alive():
        with simulation_manager.server.exceptions as exceptions:
            if exceptions:
                logger.exception(exceptions)
except KeyboardInterrupt:
    pass
finally:
    simulation_manager.stop_server()
```

```bash
2023-08-15 04:11:37,417 - INFO - Server starting on port 5000 (server.py:308)
2023-08-15 04:11:37,422 - INFO - Server started on port 5000. Press Ctrl+C to stop (server.py:292)
127.0.0.1 - - [15/Aug/2023 04:12:01] "GET / HTTP/1.1" 200 -
127.0.0.1 - - [15/Aug/2023 04:12:09] "GET / HTTP/1.1" 200 -
127.0.0.1 - - [15/Aug/2023 04:13:35] "GET / HTTP/1.1" 200 -
127.0.0.1 - - [15/Aug/2023 04:14:18] "POST /add_cash HTTP/1.1" 200 -
127.0.0.1 - - [15/Aug/2023 04:15:38] "GET /portfolio HTTP/1.1" 200 -
```

### Trading Module

```python
from dxlib.models import trading

features, labels = trading.prepare_data(data)
clf = trading.train_model(*trading.train_test_split(features, labels, 0.5))
y_pred = trading.predict_model(clf, features)
print(f"Returns: {trading.simulate_trade_allocation(y_pred, basis)[1]}")
```

### API Module

Unified data-fetching methods, ensuring consistent data structures:

```python
from dxlib.api import AlphaVantageAPI, YFinanceAPI, AlpacaMarketsAPI

# All the below calls return data in the same format
data_alpha = AlphaVantageAPI("<api_key>").get_historical_bars(["AAPL", "MSFT"])
data_yfinance = YFinanceAPI().get_historical_bars(["AAPL", "MSFT"])
data_alpaca = AlpacaMarketsAPI("<api_key>", "<api_secret>").get_historical_bars(["AAPL", "MSFT"])
```

### Data Module

### `History` Class

**Description:**  
The `History` class is a robust stock market data handler, offering a suite of utilities and technical indicators for market analysis.

- **Data Management**: Seamlessly manage your stock price data. Easily add new symbols or rows of data.
   
- **Technical Indicators**: Enjoy a rich suite of built-in technical indicators, such as:
    - Moving Averages
    - Exponential Moving Averages
    - Bollinger Bands
    - Logarithmic Changes
    - Volatility Measurements
    - Drawdown Computations

- **Data Description**: Quickly obtain a summarized description of your data with the `describe` method.

- **JSON Compatibility**: Convert your data to JSON format with a single call to the `to_json` method.

- **Extendability**: Extend the `History` class with more technical indicators or data analysis tools as per your requirements.

Here's a quick start guide to using the `History` class:

```python
from stock_market_analysis_toolkit import History
import pandas as pd

# Sample data
data = pd.DataFrame({
    'AAPL': [150, 151, 152],
    'MSFT': [300, 301, 302]
})

history = History(data)

# Adding a new stock ticker
history.add_symbol('TSLA', [650, 651, 652])

# Calculating moving averages
ma = history.moving_average(window=2)
print(ma)
```

## Contributions

We welcome improvements and extensions:

1. Fork the repository.
2. Make your enhancements.
3. Submit a pull request.

Ensure thorough testing of all changes. Your contributions will make `dxlib` even better!
