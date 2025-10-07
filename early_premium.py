import argparse, csv, os
import numpy as np
import matplotlib.pyplot as plt

from grids import s_grid_logspace, a_grid_linear
from dp_asian import DPSolverAsian

def dp_price_euro(S0, K, r, q, sigma, T, NS, NA, N, Kgh, kgrid):
    Sg = s_grid_logspace(S0, sigma, T, k=kgrid, NS=NS)
    Ag = a_grid_linear(Sg, NA=NA)
    solver = DPSolverAsian(Sg, Ag, T=T, N=N, r=r, q=q, sigma=sigma, K=K, is_call=False,
                           K_gh=Kgh, monitor_schedule=list(range(1, N+1)), exercise_schedule=[])
    price, _ = solver.price(S0=S0, A0=S0)
    return price

def dp_price_berm(S0, K, r, q, sigma, T, NS, NA, N, Kgh, kgrid, freq=5):
    # Bermudan put with exercise every `freq` steps; monitor every step.
    Sg = s_grid_logspace(S0, sigma, T, k=kgrid, NS=NS)
    Ag = a_grid_linear(Sg, NA=NA)
    monitor = list(range(1, N+1))
    exercise = [n for n in range(0, N) if (n % freq == 0 and n > 0)]
    solver = DPSolverAsian(Sg, Ag, T=T, N=N, r=r, q=q, sigma=sigma, K=K, is_call=False,
                           K_gh=Kgh, monitor_schedule=monitor, exercise_schedule=exercise)
    price, _ = solver.price(S0=S0, A0=S0)
    return price

def dp_price_amer(S0, K, r, q, sigma, T, NS, NA, N, Kgh, kgrid):
    # American put (exercise every step).
    Sg = s_grid_logspace(S0, sigma, T, k=kgrid, NS=NS)
    Ag = a_grid_linear(Sg, NA=NA)
    monitor = list(range(1, N+1))
    exercise = list(range(0, N))
    solver = DPSolverAsian(Sg, Ag, T=T, N=N, r=r, q=q, sigma=sigma, K=K, is_call=False,
                           K_gh=Kgh, monitor_schedule=monitor, exercise_schedule=exercise)
    price, _ = solver.price(S0=S0, A0=S0)
    return price

def sweep_premium_vs_M(S0,K,r,q,sigma,T,NS,NA,Kgh,kgrid,M_list,style,freq):
    rows = []
    for M in M_list:
        euro = dp_price_euro(S0,K,r,q,sigma,T,NS,NA,M,Kgh,kgrid)
        if style == "berm":
            amer = dp_price_berm(S0,K,r,q,sigma,T,NS,NA,M,Kgh,kgrid,freq=freq)
        else:
            amer = dp_price_amer(S0,K,r,q,sigma,T,NS,NA,M,Kgh,kgrid)
        rows.append({"M":M,"V_euro":euro,"V_amer":amer,"premium":amer-euro})
        print(f"M={M}: Euro={euro:.6f}, {style}={amer:.6f}, Premium={amer-euro:.6f}")
    return rows

def sweep_premium_vs_sigma(S0,K,r,q,T,NS,NA,N,Kgh,kgrid,sigmas,style,freq):
    rows = []
    for s in sigmas:
        euro = dp_price_euro(S0,K,r,q,s,T,NS,NA,N,Kgh,kgrid)
        if style == "berm":
            amer = dp_price_berm(S0,K,r,q,s,T,NS,NA,N,Kgh,kgrid,freq=freq)
        else:
            amer = dp_price_amer(S0,K,r,q,s,T,NS,NA,N,Kgh,kgrid)
        rows.append({"sigma":s,"V_euro":euro,"V_amer":amer,"premium":amer-euro})
        print(f"sigma={s:.3f}: Euro={euro:.6f}, {style}={amer:.6f}, Premium={amer-euro:.6f}")
    return rows

def sweep_premium_vs_K(S0,r,q,sigma,T,NS,NA,N,Kgh,kgrid,K_list,style,freq):
    rows = []
    for K in K_list:
        euro = dp_price_euro(S0,K,r,q,sigma,T,NS,NA,N,Kgh,kgrid)
        if style == "berm":
            amer = dp_price_berm(S0,K,r,q,sigma,T,NS,NA,N,Kgh,kgrid,freq=freq)
        else:
            amer = dp_price_amer(S0,K,r,q,sigma,T,NS,NA,N,Kgh,kgrid)
        rows.append({"K":K,"V_euro":euro,"V_amer":amer,"premium":amer-euro})
        print(f"K={K:.2f}: Euro={euro:.6f}, {style}={amer:.6f}, Premium={amer-euro:.6f}")
    return rows

def save_csv(rows, path):
    if not rows: return
    keys = list(rows[0].keys())
    with open(path,"w",newline="") as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        for r in rows: w.writerow(r)
    print("Saved", path)

def plot_premium_series(xs, ys, xlabel, title, out_png=None):
    plt.figure(figsize=(6.8,4.2))
    plt.plot(xs, ys, marker="o")
    plt.xlabel(xlabel); plt.ylabel("Early-exercise premium")
    plt.title(title); plt.grid(True, alpha=0.25)
    plt.tight_layout()
    if out_png:
        plt.savefig(out_png, dpi=180, bbox_inches="tight")
        print("Saved", out_png)
    else:
        plt.show()

def main():
    ap = argparse.ArgumentParser(description="Early-exercise premium (Bermudan/American - European) for Asian put")
    # Model
    ap.add_argument("--S0", type=float, default=100.0)
    ap.add_argument("--K", type=float, default=100.0)
    ap.add_argument("--r", type=float, default=0.05)
    ap.add_argument("--q", type=float, default=0.0)
    ap.add_argument("--T", type=float, default=1.0)
    # Discretization
    ap.add_argument("--NS", type=int, default=121)
    ap.add_argument("--NA", type=int, default=101)
    ap.add_argument("--N", type=int, default=60)
    ap.add_argument("--Kgh", type=int, default=7)
    ap.add_argument("--kgrid", type=float, default=3.0)
    # Style
    ap.add_argument("--style", choices=["berm","amer"], default="berm",
                    help="Compare Bermudan (default) or American to European")
    ap.add_argument("--freq", type=int, default=5, help="Bermudan exercise every `freq` steps")
    # What to sweep
    ap.add_argument("--do_M", action="store_true")
    ap.add_argument("--do_sigma", action="store_true")
    ap.add_argument("--do_K", action="store_true")
    ap.add_argument("--M_list", type=str, default="12,24,52")
    ap.add_argument("--sigmas", type=str, default="0.10,0.20,0.30,0.40,0.50")
    ap.add_argument("--K_list", type=str, default="70,85,100,115,130")
    # Output
    ap.add_argument("--outdir", type=str, default="premium_figs")
    args = ap.parse_args()

    os.makedirs(args.outdir, exist_ok=True)

    if args.do_M:
        Ms = [int(x) for x in args.M_list.split(",") if x.strip()]
        rows = sweep_premium_vs_M(args.S0,args.K,args.r,args.q,0.20,args.T,
                                  args.NS,args.NA,args.Kgh,args.kgrid,Ms,args.style,args.freq)
        save_csv(rows, os.path.join(args.outdir, "premium_vs_M.csv"))
        plot_premium_series([r["M"] for r in rows], [r["premium"] for r in rows],
                            "Monitoring dates M",
                            f"Premium vs M ({args.style})",
                            out_png=os.path.join(args.outdir, "premium_vs_M.png"))

    if args.do_sigma:
        sigs = [float(x) for x in args.sigmas.split(",") if x.strip()]
        rows = sweep_premium_vs_sigma(args.S0,args.K,args.r,args.q,args.T,
                                      args.NS,args.NA,args.N,args.Kgh,args.kgrid,sigs,args.style,args.freq)
        save_csv(rows, os.path.join(args.outdir, "premium_vs_sigma.csv"))
        plot_premium_series([r["sigma"] for r in rows], [r["premium"] for r in rows],
                            "Volatility sigma",
                            f"Premium vs sigma ({args.style})",
                            out_png=os.path.join(args.outdir, "premium_vs_sigma.png"))

    if args.do_K:
        Ks = [float(x) for x in args.K_list.split(",") if x.strip()]
        rows = sweep_premium_vs_K(args.S0,args.r,args.q,0.20,args.T,
                                  args.NS,args.NA,args.N,args.Kgh,args.kgrid,Ks,args.style,args.freq)
        save_csv(rows, os.path.join(args.outdir, "premium_vs_K.csv"))
        plot_premium_series([r["K"] for r in rows], [r["premium"] for r in rows],
                            "Strike K",
                            f"Premium vs K ({args.style})",
                            out_png=os.path.join(args.outdir, "premium_vs_K.png"))

if __name__ == "__main__":
    main()