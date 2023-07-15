# Quantitative Analysis library

Contains basic methods, interfaces and integration calls
for statistical tools, as well as for data gathering functions.


## Installation

`pip install dxlib`


## Quickstart

### Research Module
```
from dxlib import finite_differences

import numpy
import matplotlib.pyplot

x = np.arange(-3, 3, h)
y = np.tanh(x)

dy = finite_differences(x, y)
```

### Simulation Module


### API Module

```
from dxlib.api import AlphaVantageAPI as av

print("Realtime exchange rates from the last 5 minutes:")

alpha_vantage = av("<api_key>")
for i in range(5):
  currencies_to_query = ['JPY', 'EUR', 'GBP', 'CAD', 'AUD']
  exchange_rates_df = api.fetch_currency_exchange_rates(currencies_to_query)
  print(terminal, exchange_rates_df)
  time.sleep(60)
```

### Data Module

A visual graph of the finite differences should be plotted,
and the numerical values for the differentiation at the point x
returned.
