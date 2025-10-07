#!/usr/bin/env python3
import argparse, os, csv
import numpy as np
import matplotlib.pyplot as plt

from grids import s_grid_logspace, a_grid_linear
from dp_asian import DPSolverAsian

def dp_price(S0, K, r, q, sigma, T, NS, NA, N, Kgh, kgrid, style="euro", berm_freq=5, is_call=False):
    Sg = s_grid_logspace(S0, sigma, T, k=kgrid, NS=NS)
    Ag = a_grid_linear(Sg, NA=NA)
    monitor = list(range(1, N+1))
    if style == "euro":
        exercise = []
    elif style == "berm":
        exercise = [n for n in range(0, N) if (n % berm_freq == 0 and n > 0)]
    elif style == "amer":
        exercise = list(range(0, N))
    else:
        raise ValueError("style must be euro|berm|amer")
    solver = DPSolverAsian(Sg, Ag, T=T, N=N, r=r, q=q, sigma=sigma, K=K, is_call=is_call,
                           K_gh=Kgh, monitor_schedule=monitor, exercise_schedule=exercise)
    price, _ = solver.price(S0=S0, A0=S0)
    return price

def overlay_plot(xs, ys_dict, xlabel, title, out_png=None):
    plt.figure(figsize=(7.2, 4.4))
    order = ["euro", "berm", "amer"]
    labels = {"euro":"European", "berm":"Bermudan", "amer":"American"}
    markers = {"euro":"o", "berm":"s", "amer":"^"}
    for k in order:
        if k in ys_dict:
            plt.plot(xs, ys_dict[k], marker=markers[k], label=labels[k])
    plt.xlabel(xlabel); plt.ylabel("Price")
    plt.title(title)
    plt.grid(True, alpha=0.25)
    plt.legend()
    plt.tight_layout()
    if out_png:
        plt.savefig(out_png, dpi=200, bbox_inches="tight")
        print("Saved", out_png)
    else:
        plt.show()

def write_csv(xs, ys_dict, xname, out_csv):
    keys = ["style", xname, "price"]
    with open(out_csv, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        for style, ys in ys_dict.items():
            for x, y in zip(xs, ys):
                w.writerow({"style": style, xname: x, "price": y})
    print("Saved", out_csv)

def main():
    ap = argparse.ArgumentParser(description="Overlay sensitivity plots: European vs Bermudan vs American")
    # Model
    ap.add_argument("--S0", type=float, default=100.0)
    ap.add_argument("--K", type=float, default=100.0)
    ap.add_argument("--r", type=float, default=0.05)
    ap.add_argument("--q", type=float, default=0.0)
    ap.add_argument("--sigma", type=float, default=0.20)
    ap.add_argument("--T", type=float, default=1.0)
    ap.add_argument("--call", action="store_true")
    # DP discretization
    ap.add_argument("--NS", type=int, default=121)
    ap.add_argument("--NA", type=int, default=101)
    ap.add_argument("--N", type=int, default=60)
    ap.add_argument("--Kgh", type=int, default=7)
    ap.add_argument("--kgrid", type=float, default=3.0)
    # Bermudan frequency
    ap.add_argument("--berm_freq", type=int, default=5)
    # Sweep grids
    ap.add_argument("--sigmas", type=str, default="0.10,0.20,0.30,0.40,0.50")
    ap.add_argument("--rates", type=str, default="0.00,0.02,0.05,0.08")
    ap.add_argument("--strikes", type=str, default="80,90,100,110,120")
    ap.add_argument("--M_list", type=str, default="12,24,52")
    # Output
    ap.add_argument("--outdir", type=str, default="sensitivity_overlay")
    args = ap.parse_args()

    os.makedirs(args.outdir, exist_ok=True)

    # Helper to evaluate the three styles
    def eval_three(fn_build):
        vals = {}
        for style in ["euro","berm","amer"]:
            vals[style] = fn_build(style)
        return vals

    # 1) vs sigma
    sigmas = [float(x) for x in args.sigmas.split(",") if x.strip()]
    ys_dict = eval_three(lambda style: [
        dp_price(args.S0, args.K, args.r, args.q, s, args.T, args.NS, args.NA, args.N, args.Kgh, args.kgrid,
                 style=style, berm_freq=args.berm_freq, is_call=args.call)
        for s in sigmas
    ])
    write_csv(sigmas, ys_dict, "sigma", os.path.join(args.outdir, "price_vs_sigma.csv"))
    overlay_plot(sigmas, ys_dict, "Volatility σ", "Price vs σ (European vs Bermudan vs American)",
                 out_png=os.path.join(args.outdir, "price_vs_sigma.png"))

    # 2) vs r
    rates = [float(x) for x in args.rates.split(",") if x.strip()]
    ys_dict = eval_three(lambda style: [
        dp_price(args.S0, args.K, r, args.q, args.sigma, args.T, args.NS, args.NA, args.N, args.Kgh, args.kgrid,
                 style=style, berm_freq=args.berm_freq, is_call=args.call)
        for r in rates
    ])
    write_csv(rates, ys_dict, "r", os.path.join(args.outdir, "price_vs_r.csv"))
    overlay_plot(rates, ys_dict, "Rate r", "Price vs r (European vs Bermudan vs American)",
                 out_png=os.path.join(args.outdir, "price_vs_r.png"))

    # 3) vs K
    strikes = [float(x) for x in args.strikes.split(",") if x.strip()]
    ys_dict = eval_three(lambda style: [
        dp_price(args.S0, K, args.r, args.q, args.sigma, args.T, args.NS, args.NA, args.N, args.Kgh, args.kgrid,
                 style=style, berm_freq=args.berm_freq, is_call=args.call)
        for K in strikes
    ])
    write_csv(strikes, ys_dict, "K", os.path.join(args.outdir, "price_vs_K.csv"))
    overlay_plot(strikes, ys_dict, "Strike K", "Price vs K (European vs Bermudan vs American)",
                 out_png=os.path.join(args.outdir, "price_vs_K.png"))

    # 4) vs M (set N=M)
    Ms = [int(x) for x in args.M_list.split(",") if x.strip()]
    ys_dict = {}
    for style in ["euro","berm","amer"]:
        ys = []
        for M in Ms:
            ys.append(dp_price(args.S0, args.K, args.r, args.q, args.sigma, args.T, args.NS, args.NA, M, args.Kgh, args.kgrid,
                               style=style, berm_freq=args.berm_freq, is_call=args.call))
        ys_dict[style] = ys
    write_csv(Ms, ys_dict, "M", os.path.join(args.outdir, "price_vs_M.csv"))
    overlay_plot(Ms, ys_dict, "Monitoring dates M", "Price vs M (European vs Bermudan vs American)",
                 out_png=os.path.join(args.outdir, "price_vs_M.png"))

if __name__ == "__main__":
    main()