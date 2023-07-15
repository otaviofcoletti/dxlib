# Quantitative Analysis library

This library contains basic methods, interfaces, and integration calls for statistical tools, as well as data gathering functions.

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install dxlib.

```bash
pip install dxlib
```

## Quickstart

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
[Note: The Simulation Module's example needs to be provided]

### Trading Module
```python
from dxlib.models import trading

features, labels = trading.prepare_data(data)
train, test = trading.train_test_split(features, labels, 0.5)
clf = trading.train_model(train["x"], train["y"])
y_pred = trading.predict_model(clf, features)
pred_changes, returns = trading.simulate_trade_allocation(y_pred, basis)
print(f"Predicted changes: {pred_changes}, \nReturns: {returns}")
```
Sample Output:
```
Predicted changes: [0.01, -0.02, 0.03, ...]
Returns: 0.07
```

### API Module
```python
from dxlib.api import AlphaVantageAPI as av

print("Realtime exchange rates from the last 5 minutes:")

alpha_vantage = av("<api_key>")
for i in range(5):
  currencies_to_query = ['JPY', 'EUR', 'GBP', 'CAD', 'AUD']
  exchange_rates_df = alpha_vantage.fetch_currency_exchange_rates(currencies_to_query)
  print(exchange_rates_df)
  time.sleep(60)
```
Sample Output:
```
Realtime exchange rates from the last 5 minutes:
   JPY     EUR     GBP     CAD     AUD
0  103.76  0.83   0.72   1.27   1.32
1  103.76  0.83   0.72   1.27   1.32
2  103.75  0.83   0.72   1.27   1.32
3  103.76  0.83   0.72   1.27   1.32
4  103.77  0.83   0.72   1.27   1.32
```

### Data Module
...

Note: In the finite differences method, the numerical values for the differentiation at the point x are returned, and a visual graph of the finite differences can be plotted using matplotlib.
For the API module, replace "<api_key>" with your AlphaVantage API key. The module will fetch real-time exchange rates for the past five minutes for the specified currencies.

## Contribution

Contributions are welcome! If you're interested in contributing, feel free to fork the repository and submit a pull request. Please make sure to test the changes thoroughly. We're looking forward to your enhancements!
