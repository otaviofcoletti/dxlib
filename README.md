# Quantitative Analysis library

Contains basic methods, interfaces and integration calls
for statistical tools, as well as for data gathering functions.


## Installation

`pip install dxlib`


## Quickstart

```
from dxlib import finite_differences

import numpy
import matplotlib.pyplot

x = np.arange(-3, 3, h)
y = np.tanh(x)

dy = finite_differences(x, y)
```

A visual graph of the finite differences should be plotted,
and the numerical values for the differentiation at the point x
returned.