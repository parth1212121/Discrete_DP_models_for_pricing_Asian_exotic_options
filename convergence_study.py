#!/usr/bin/env python3

import argparse, csv, time
import numpy as np
import matplotlib.pyplot as plt

from grids import s_grid_logspace, a_grid_linear
from dp_asian import DPSolverAsian
from mc_asian import asian_euro_mc

def run_dp_once(S0, K, r, q, sigma, T, NS, NA, N, Kgh, kgrid):
    Sg = s_grid_logspace(S0, sigma, T, k=kgrid, NS=NS)
    Ag = a_grid_linear(Sg, NA=NA)
    solver = DPSolverAsian(Sg, Ag, T=T, N=N, r=r, q=q, sigma=sigma, K=K,
                           is_call=True, K_gh=Kgh,
                           monitor_schedule=list(range(1, N+1)),  # monitor every step
                           exercise_schedule=[])  # European
    t0 = time.perf_counter()
    price, _ = solver.price(S0=S0, A0=S0, return_frontier=False)
    t1 = time.perf_counter()
    return price, (t1 - t0)

def run_mc_once(S0, K, r, q, sigma, T, M, paths, seed):
    est, (lo, hi), se = asian_euro_mc(S0, K, r, sigma, T, M, paths=paths, q=q, call=True, seed=seed)
    half = hi - est
    return est, half, se

def sweep(param, values, S0, K, r, q, sigma, T, NS, NA, N, Kgh, kgrid, mc_paths, seed):
    rows = []
    # MC baseline uses monitoring M = N for consistency; if we sweep N, we keep MC in sync with N
    for v in values:
        NSv, NAv, Nv, Kghv = NS, NA, N, Kgh
        if param == "NS": NSv = int(v)
        elif param == "NA": NAv = int(v)
        elif param == "N": Nv = int(v)
        elif param == "Kgh": Kghv = int(v)
        else: raise ValueError("param must be one of NS, NA, N, Kgh")

        # DP
        dp_price, dt = run_dp_once(S0, K, r, q, sigma, T, NSv, NAv, Nv, Kghv, kgrid)
        # MC baseline (European) with M = Nv monitors
        mc_mean, mc_half, se = run_mc_once(S0, K, r, q, sigma, T, Nv, mc_paths, seed)

        err = abs(dp_price - mc_mean)
        rows.append({
            "param": param,
            "value": v,
            "NS": NSv, "NA": NAv, "N": Nv, "Kgh": Kghv,
            "dp_price": dp_price,
            "mc_mean": mc_mean,
            "mc_CI_half": mc_half,
            "abs_error": err,
            "dp_runtime_s": dt
        })
        print(f"{param}={v}: DP={dp_price:.6f}, MC={mc_mean:.6f}±{mc_half:.6f}, |err|={err:.6f}, time={dt:.3f}s")

    return rows

def save_csv(rows, out_csv):
    if not rows: return
    keys = list(rows[0].keys())
    with open(out_csv, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        for r in rows: w.writerow(r)
    print("Saved", out_csv)

def plot_convergence(rows, title_prefix, out_png=None):
    xs = [r["value"] for r in rows]
    err = [r["abs_error"] for r in rows]
    ci = [r["mc_CI_half"] for r in rows]
    rt = [r["dp_runtime_s"] for r in rows]

    fig, ax = plt.subplots(1, 2, figsize=(10,4))

    ax[0].plot(xs, err, marker="o")
    ax[0].plot(xs, ci, marker="x", linestyle="--", alpha=0.6, label="MC CI half-width")
    ax[0].set_xlabel(rows[0]["param"])
    ax[0].set_ylabel("Absolute error |DP - MC|")
    ax[0].set_title(f"{title_prefix}: Error vs {rows[0]['param']}")
    ax[0].legend()

    ax[1].plot(xs, rt, marker="o")
    ax[1].set_xlabel(rows[0]["param"])
    ax[1].set_ylabel("DP runtime (s)")
    ax[1].set_title(f"{title_prefix}: Runtime vs {rows[0]['param']}")
    fig.tight_layout()

    if out_png:
        plt.savefig(out_png, dpi=160)
        print("Saved", out_png)
    else:
        plt.show()

def main():
    ap = argparse.ArgumentParser(description="Convergence study for DP vs MC (European Asian)")
    # Model
    ap.add_argument("--S0", type=float, default=100.0)
    ap.add_argument("--K", type=float, default=100.0)
    ap.add_argument("--r", type=float, default=0.05)
    ap.add_argument("--q", type=float, default=0.0)
    ap.add_argument("--sigma", type=float, default=0.20)
    ap.add_argument("--T", type=float, default=1.0)
    # Baseline discretization
    ap.add_argument("--NS", type=int, default=201)
    ap.add_argument("--NA", type=int, default=141)
    ap.add_argument("--N", type=int, default=60)
    ap.add_argument("--Kgh", type=int, default=7)
    ap.add_argument("--kgrid", type=float, default=3.0)
    # Sweep control
    ap.add_argument("--param", choices=["NS", "NA", "N", "Kgh"], default="NS")
    ap.add_argument("--values", type=str, default="81,101,121,161,201")
    # MC
    ap.add_argument("--mc_paths", type=int, default=100000)
    ap.add_argument("--seed", type=int, default=2025)
    # Output
    ap.add_argument("--out_csv", type=str, default="convergence_results.csv")
    ap.add_argument("--out_png", type=str, default="convergence_plot.png")
    args = ap.parse_args()

    values = [int(v) for v in args.values.split(",") if v.strip()]

    rows = sweep(args.param, values, args.S0, args.K, args.r, args.q, args.sigma, args.T,
                 args.NS, args.NA, args.N, args.Kgh, args.kgrid, args.mc_paths, args.seed)

    save_csv(rows, args.out_csv)
    plot_convergence(rows, title_prefix=f"S0={args.S0}, K={args.K}, sigma={args.sigma}", out_png=args.out_png)

if __name__ == "__main__":
    main()
