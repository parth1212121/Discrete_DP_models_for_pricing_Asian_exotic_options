import numpy as np
from typing import Optional, Tuple, List
from gh import gh_nodes_weights
from interp2d import bilinear
from math import sqrt, pi
class DPSolverAsian:
    def __init__(self, S_grid, A_grid, T: float, N: int, r: float, q: float, sigma: float,
                 K: float, is_call: bool, K_gh: int = 7,
                 monitor_schedule: Optional[List[int]] = None,
                 exercise_schedule: Optional[List[int]] = None):
        self.Sg = np.array(S_grid, dtype=float)
        self.Ag = np.array(A_grid, dtype=float)
        self.NS, self.NA = len(self.Sg), len(self.Ag)
        self.T = float(T); self.N = int(N)
        self.dt = self.T / self.N
        self.r = float(r); self.q = float(q); self.sigma = float(sigma)
        self.K = float(K); self.is_call = bool(is_call)
        self.K_gh = int(K_gh)
        self.monitor_schedule = set(range(1, self.N+1)) if monitor_schedule is None else set(monitor_schedule)
        self.exercise_schedule = set() if exercise_schedule is None else set(exercise_schedule)
        self.mu = (self.r - self.q - 0.5*self.sigma**2) * self.dt
        self.nu = self.sigma * np.sqrt(self.dt)
        self.x_gh, self.w_gh = gh_nodes_weights(self.K_gh)
    def payoff(self, S, A):
        return max(A - self.K, 0.0) if self.is_call else max(self.K - A, 0.0)
    def _payoff_grid(self):
        V = np.zeros((self.NS, self.NA), dtype=float)
        for i in range(self.NS):
            for j in range(self.NA):
                V[i, j] = self.payoff(self.Sg[i], self.Ag[j])
        return V
    def price(self, S0: float, A0: float, return_frontier: bool = False):
        disc = np.exp(-self.r * self.dt)
        V_next = self._payoff_grid()
        frontier_masks = []
        for n in range(self.N-1, -1, -1):
            k_prev = sum(1 for idx in range(1, n+1) if idx in self.monitor_schedule)
            V_now = np.empty_like(V_next)
            Zk = np.sqrt(2.0) * self.x_gh
            drift = self.mu; vol = self.nu
            exercise_mask = np.zeros_like(V_now, dtype=bool) if (n in self.exercise_schedule) else None
            for i in range(self.NS):
                Si = self.Sg[i]
                for j in range(self.NA):
                    Aj = self.Ag[j]
                    acc = 0.0
                    for m in range(self.K_gh):
                        Z = Zk[m]
                        Sp = Si * np.exp(drift + vol * Z)
                        if (n+1) in self.monitor_schedule:
                            kp = k_prev
                            Ap = (kp * Aj + Sp) / (kp + 1)
                        else:
                            Ap = Aj
                        Vp = bilinear(V_next, self.Sg, self.Ag, Sp, Ap)
                        acc += self.w_gh[m] * Vp
                    cont = disc * acc / np.sqrt(np.pi)
                    if n in self.exercise_schedule:
                        ex = self.payoff(Si, Aj)
                        V_now[i, j] = ex if ex > cont else cont
                        if exercise_mask is not None:
                            exercise_mask[i, j] = (ex >= cont)
                    else:
                        V_now[i, j] = cont
            V_next = V_now
            if exercise_mask is not None and return_frontier:
                frontier_masks.append(exercise_mask)
        price0 = bilinear(V_next, self.Sg, self.Ag, S0, A0)
        if return_frontier:
            return price0, frontier_masks[::-1]
        else:
            return price0, None
