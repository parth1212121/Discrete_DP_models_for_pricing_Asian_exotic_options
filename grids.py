import numpy as np

def s_grid_logspace(S0: float, sigma: float, T: float, k: float = 3.0, NS: int = 121):
    rng = k * sigma * np.sqrt(T)
    Smin = S0 * np.exp(-rng)
    Smax = S0 * np.exp(+rng)
    x = np.linspace(np.log(Smin), np.log(Smax), NS)
    return np.exp(x)
def a_grid_linear(S_grid, NA: int = 101):
    return np.linspace(float(S_grid.min()), float(S_grid.max()), NA)
