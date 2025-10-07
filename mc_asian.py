import numpy as np

def asian_euro_mc(S0, K, r, sigma, T, M, paths=100_000, q=0.0, call=True, seed=42, antithetic=True):
    rng = np.random.default_rng(seed)
    dt = T / M
    nudt = (r - q - 0.5 * sigma**2) * dt
    sigsdt = sigma * np.sqrt(dt)
    disc = np.exp(-r * T)
    if antithetic:
        assert paths % 2 == 0
        half = paths // 2
        Z = rng.standard_normal(size=(half, M))
        Zanti = -Z
        p1 = _asian_payoffs_from_Z(S0, K, nudt, sigsdt, Z, M, call)
        p2 = _asian_payoffs_from_Z(S0, K, nudt, sigsdt, Zanti, M, call)
        payoff = 0.5 * (p1 + p2)
    else:
        Z = rng.standard_normal(size=(paths, M))
        payoff = _asian_payoffs_from_Z(S0, K, nudt, sigsdt, Z, M, call)
    payoff_disc = disc * payoff
    est = payoff_disc.mean()
    se = payoff_disc.std(ddof=1) / np.sqrt(payoff_disc.shape[0])
    ci = (est - 1.96*se, est + 1.96*se)
    return est, ci, se
def _asian_payoffs_from_Z(S0, K, nudt, sigsdt, Z, M, call=True):
    P = Z.shape[0]
    S = np.full(P, S0, dtype=float)
    acc = np.zeros(P, dtype=float)
    for k in range(M):
        S *= np.exp(nudt + sigsdt * Z[:, k])
        acc += S
    A = acc / M
    return np.maximum(A - K, 0.0) if call else np.maximum(K - A, 0.0)
