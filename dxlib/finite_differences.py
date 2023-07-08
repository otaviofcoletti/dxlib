import numpy as np
import matplotlib.pyplot as plt


def finite_differences(x, y):
    range_x = x[:-1]

    finite_difference = np.diff(y) / abs(x[1] - x[0])

    plt.plot(range_x, finite_difference, '--', label='Approximation')
    plt.legend()
    plt.show()
