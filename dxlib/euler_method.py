import numpy as np
import matplotlib.pyplot as plt


def euler_method(x, f, starting_point=0):
    s = np.zeros(len(x))
    s[0] = starting_point
    delta = abs(x[1] - x[0])

    for i in range(0, len(x) - 1):
        s[i + 1] = s[i] + delta * f(x[i], s[i])

    plt.plot(x, s, 'bo--', label='Approximation')
    plt.xlabel('x')
    plt.ylabel('f(x) = y')
    plt.grid()
    plt.show()
