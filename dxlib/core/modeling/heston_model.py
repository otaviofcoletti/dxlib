# Heston Model
import numpy as np
import scipy.optimize as so


class HestonModel:
    def __init__(self, s0, v0, theta, kappa, sigma, rho):
        self.s0 = s0
        self.v0 = v0
        self.theta = theta
        self.kappa = kappa
        self.sigma = sigma
        self.rho = rho

    def process(self, t, n, m):
        d_s = np.zeros((n, m))

        w1 = np.random.normal(size=(n, m))
        w2 = self.rho * w1 + np.sqrt(1 - self.rho ** 2) * np.random.normal(size=(n, m))

        d_s[:, 0] = self.s0
        for i in range(1, m):
            dt = t[i] - t[i - 1]
            d_s[:, i] = d_s[:, i - 1] * np.exp(
                np.sqrt(self.v0 * np.exp(self.theta * dt) / self.kappa) * w1[:, i]
                - 0.5 * self.v0 * np.exp(self.theta * dt) * dt
            )

        d_v = np.zeros((n, m))
        d_v[:, 0] = self.v0
        for i in range(1, m):
            dt = t[i] - t[i - 1]
            d_v[:, i] = d_v[:, i - 1] + self.kappa * (self.theta - d_v[:, i - 1]) * dt + self.sigma * np.sqrt(
                d_v[:, i - 1] * dt) * w2[:, i]

        return d_s, d_v

    def option_price(self, t, m, k, cp):
        paths, vols = self.process(t, 100000, m)
        payoff = np.maximum(cp * (paths[:, -1] - k), 0)
        return np.mean(payoff) * np.exp(-0.05 * t[-1])

    def implied_vol(self, t, m, k, cp, p):
        array = np.vectorize(lambda x: self.option_price(t, m, x, cp) - p)(k)
        return so.fsolve(lambda x: self.option_price(t, m, k, cp) - p, array)

    def implied_vol_surface(self, t, m, k, cp, p):
        return np.vectorize(lambda x: self.implied_vol(t, m, x, cp, p))(k)

    def option_price_surface(self, t, m, k, cp):
        return np.vectorize(lambda x: self.option_price(t, m, x, cp))(k)
