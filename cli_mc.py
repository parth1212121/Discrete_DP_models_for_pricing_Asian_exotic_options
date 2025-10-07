#!/usr/bin/env python3
import argparse
from mc_asian import asian_euro_mc
def main():
    p = argparse.ArgumentParser(description='MC baseline for European arithmetic Asian')
    p.add_argument('--S0', type=float, required=True)
    p.add_argument('--K', type=float, required=True)
    p.add_argument('--r', type=float, required=True)
    p.add_argument('--sigma', type=float, required=True)
    p.add_argument('--T', type=float, required=True)
    p.add_argument('--M', type=int, required=True)
    p.add_argument('--paths', type=int, default=100000)
    p.add_argument('--q', type=float, default=0.0)
    p.add_argument('--call', action='store_true')
    p.add_argument('--seed', type=int, default=2025)
    args = p.parse_args()
    est, (lo, hi), se = asian_euro_mc(args.S0, args.K, args.r, args.sigma, args.T, args.M,
                                      paths=args.paths, q=args.q, call=args.call, seed=args.seed)
    print(f'MC estimate: {est:.6f}  95%CI=({lo:.6f}, {hi:.6f})  SE={se:.6f}')
if __name__ == '__main__':
    main()
