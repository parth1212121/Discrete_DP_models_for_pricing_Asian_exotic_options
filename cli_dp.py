#!/usr/bin/env python3
import argparse
from grids import s_grid_logspace, a_grid_linear
from dp_asian import DPSolverAsian
def main():
    p = argparse.ArgumentParser(description='DP pricer for Asian options')
    p.add_argument('--S0', type=float, required=True); p.add_argument('--A0', type=float, default=None)
    p.add_argument('--K', type=float, required=True); p.add_argument('--r', type=float, required=True)
    p.add_argument('--q', type=float, default=0.0); p.add_argument('--sigma', type=float, required=True)
    p.add_argument('--T', type=float, required=True); p.add_argument('--NS', type=int, default=121)
    p.add_argument('--NA', type=int, default=101); p.add_argument('--steps', type=int, default=60)
    p.add_argument('--gh', type=int, default=7); p.add_argument('--kgrid', type=float, default=3.0)
    p.add_argument('--call', action='store_true')
    p.add_argument('--monitor', type=str, default='all')
    p.add_argument('--exercise', type=str, default='')
    args = p.parse_args()
    Sg = s_grid_logspace(args.S0, args.sigma, args.T, k=args.kgrid, NS=args.NS)
    Ag = a_grid_linear(Sg, NA=args.NA)
    A0 = args.S0 if args.A0 is None else args.A0
    monitor = list(range(1, args.steps+1)) if args.monitor=='all' else [int(x) for x in args.monitor.split(',') if x.strip()]
    if args.exercise=='': exercise=[]
    elif args.exercise=='all': exercise=list(range(0, args.steps))
    else: exercise=[int(x) for x in args.exercise.split(',') if x.strip()]
    solver = DPSolverAsian(Sg, Ag, T=args.T, N=args.steps, r=args.r, q=args.q, sigma=args.sigma,
                           K=args.K, is_call=args.call, K_gh=args.gh,
                           monitor_schedule=monitor, exercise_schedule=exercise)
    price, _ = solver.price(S0=args.S0, A0=A0, return_frontier=False)
    print(f'DP price: {price:.6f}')
if __name__ == '__main__':
    main()
