import numpy as np


def finite_differences(x, y):
    range_x = x[:-1]

    finite_difference = np.diff(y) / abs(x[1] - x[0])
    return finite_difference, range_x
