import numpy as np
from numpy.polynomial.hermite import hermgauss
from math import sqrt, pi

def gh_nodes_weights(K: int):
    if K < 2:
        raise ValueError('K must be >= 2')
    x, w = hermgauss(K)
    return x, w

def gh_expectation(func, K: int):
    x, w = gh_nodes_weights(K)
    vals = func(np.sqrt(2.0) * x)
    return (w @ vals) / np.sqrt(pi)
