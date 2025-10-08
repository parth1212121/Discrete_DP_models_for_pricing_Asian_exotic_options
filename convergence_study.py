#!/usr/bin/env python3

import argparse, csv, time, os
import numpy as np
import matplotlib.pyplot as plt

from grids import s_grid_logspace, a_grid_linear
from dp_asian import DPSolverAsian
from mc_asian import asian_euro_mc


# -----------------------------------------------------------
# Utility Functions
# -----------------------------------------------------------

def ensure_dir(filepath):
    """Ensure that the directory for the given file path exists."""
    directory = os.path.dirname(os.path.abspath(filepath))
    if directory and not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)


# -----------------------------------------------------------
# Core Simulation Functions
# -----------------------------------------------------------

def run_dp_once(S0, K, r, q, sigma, T, NS, NA, N, Kgh, kgrid):
    """Run one DP pricing for given discretization parameters."""
    Sg = s_grid_logspace(S0, sigma, T, k=kgrid, NS=NS)
    Ag = a_grid_linear(Sg, NA=NA)
    solver = DPSolverAsian(Sg, Ag, T=T, N=N, r=r, q=q, sigma=sigma, K=K,
                           is_call=True, K_gh=Kgh,
                           monitor_schedule=list(range(1, N+1)),
                           exercise_schedule=[])  # European only
    t0 = time.perf_counter()
    price, _ = solver.price(S0=S0, A0=S0, return_frontier=False)
    t1 = time.perf_counter()
    return price, (t1 - t0)


def run_mc_once(S0, K, r, q, sigma, T, M, paths, seed):
    """Monte Carlo baseline for European Asian option."""
    est, (lo, hi), se = asian_euro_mc(S0, K, r, sigma, T, M, paths=paths, q=q, call=True, seed=seed)
    half = hi - est
    return est, half, se


def sweep(param, values, S0, K, r, q, sigma, T, NS, NA, N, Kgh, kgrid, mc_paths, seed):
    """Sweep one parameter (NS, NA, N, Kgh) and collect errors."""
    rows = []
    for v in values:
        NSv, NAv, Nv, Kghv = NS, NA, N, Kgh
        if param == "NS": NSv = int(v)
        elif param == "NA": NAv = int(v)
        elif param == "N": Nv = int(v)
        elif param == "Kgh": Kghv = int(v)
        else:
            raise ValueError("param must be one of NS, NA, N, Kgh")

        dp_price, dt = run_dp_once(S0, K, r, q, sigma, T, NSv, NAv, Nv, Kghv, kgrid)
        mc_mean, mc_half, se = run_mc_once(S0, K, r, q, sigma, T, Nv, mc_paths, seed)
        err = abs(dp_price - mc_mean)

        rows.append({
            "param": param, "value": v,
            "dp_price": dp_price, "mc_mean": mc_mean,
            "mc_CI_half": mc_half, "abs_error": err, "runtime_s": dt
        })
        print(f"{param}={v}: DP={dp_price:.6f}, MC={mc_mean:.6f}±{mc_half:.6f}, |err|={err:.6f}")
    return rows


# -----------------------------------------------------------
# Plotting & Saving
# -----------------------------------------------------------

def save_csv(rows, out_csv):
    """Save results to CSV file."""
    if not rows:
        return
    ensure_dir(out_csv)
    keys = list(rows[0].keys())
    with open(out_csv, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        for r in rows:
            w.writerow(r)
    print("Saved", out_csv)


def plot_convergence(rows, title_prefix, out_png=None):
    """Plot absolute error vs discretization parameter (no runtime)."""
    xs = [r["value"] for r in rows]
    err = [r["abs_error"] for r in rows]
    ci = [r["mc_CI_half"] for r in rows]

    plt.figure(figsize=(7, 4))
    plt.plot(xs, err, marker="o", label="|DP - MC|", linewidth=2)
    plt.plot(xs, ci, marker="x", linestyle="--", alpha=0.7, label="MC CI half-width")
    plt.xlabel(rows[0]["param"])
    plt.ylabel("Absolute error |DP - MC|")
    plt.title(f"{title_prefix}: Error vs {rows[0]['param']}")
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()

    if out_png:
        ensure_dir(out_png)
        plt.savefig(out_png, dpi=180, bbox_inches="tight")
        print("Saved", out_png)
    else:
        plt.show()


# -----------------------------------------------------------
# Main
# -----------------------------------------------------------

def main():
    ap = argparse.ArgumentParser(description="Convergence study for DP vs MC (European Asian)")
    # Model parameters
    ap.add_argument("--S0", type=float, default=100.0)
    ap.add_argument("--K", type=float, default=100.0)
    ap.add_argument("--r", type=float, default=0.05)
    ap.add_argument("--q", type=float, default=0.0)
    ap.add_argument("--sigma", type=float, default=0.20)
    ap.add_argument("--T", type=float, default=1.0)
    # Discretization
    ap.add_argument("--NS", type=int, default=201)
    ap.add_argument("--NA", type=int, default=141)
    ap.add_argument("--N", type=int, default=60)
    ap.add_argument("--Kgh", type=int, default=7)
    ap.add_argument("--kgrid", type=float, default=3.0)
    # Sweep control
    ap.add_argument("--param", choices=["NS", "NA", "N", "Kgh"], default="NS")
    ap.add_argument("--values", type=str, default="81,101,121,161,201")
    # Monte Carlo
    ap.add_argument("--mc_paths", type=int, default=100000)
    ap.add_argument("--seed", type=int, default=2025)
    # Output (auto-named based on param)
    ap.add_argument("--outdir", type=str, default="convergence_figs")
    args = ap.parse_args()

    ensure_dir(args.outdir)
    out_csv = os.path.join(args.outdir, f"conv_{args.param}.csv")
    out_png = os.path.join(args.outdir, f"conv_{args.param}.png")

    values = [int(v) for v in args.values.split(",") if v.strip()]

    rows = sweep(args.param, values, args.S0, args.K, args.r, args.q,
                 args.sigma, args.T, args.NS, args.NA, args.N,
                 args.Kgh, args.kgrid, args.mc_paths, args.seed)

    save_csv(rows, out_csv)
    plot_convergence(rows, title_prefix=f"S0={args.S0}, K={args.K}, sigma={args.sigma}", out_png=out_png)


if __name__ == "__main__":
    main()
