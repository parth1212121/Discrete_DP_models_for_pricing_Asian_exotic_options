#!/usr/bin/env python3
import os
import numpy as np
import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter

from grids import s_grid_logspace, a_grid_linear
from dp_asian import DPSolverAsian

def _grid_edges_from_centers(centers):
    c = np.asarray(centers, dtype=float)
    e = np.empty(len(c) + 1, dtype=float)
    e[1:-1] = 0.5 * (c[:-1] + c[1:])
    e[0]    = c[0] - (e[1] - c[0])
    e[-1]   = c[-1] + (c[-1] - e[-2])
    return e

def plot_frontier_clean(mask, Sg, Ag, title, savepath=None, smooth_sigma=0.0):
    Z = mask.T.astype(float)  # (NA, NS)

    # Cell edges for pcolormesh
    S_edges = _grid_edges_from_centers(Sg)
    A_edges = _grid_edges_from_centers(Ag)

    fig, ax = plt.subplots(figsize=(7.2, 5.0))

    # Heatmap with exact pixel edges; no interpolation
    pcm = ax.pcolormesh(S_edges, A_edges, Z, shading='flat')

    # Optional light smoothing for a crisp single contour line
    Zplot = Z if smooth_sigma <= 0 else gaussian_filter(Z, sigma=smooth_sigma)

    # Contour on centers
    Sg_mesh, Ag_mesh = np.meshgrid(Sg, Ag, indexing='xy')
    CS = ax.contour(Sg_mesh, Ag_mesh, Zplot, levels=[0.5], linewidths=1.5)

    ax.set_xlabel("S")
    ax.set_ylabel("A")
    ax.set_title(title)
    cbar = fig.colorbar(pcm, ax=ax)
    cbar.set_label("Exercise (1) / Continue (0)")
    fig.tight_layout()

    if savepath:
        root, ext = os.path.splitext(savepath)
        png_path = root + ".png"
        pdf_path = root + ".pdf"
        fig.savefig(png_path, dpi=300, bbox_inches="tight")
        fig.savefig(pdf_path, dpi=300, bbox_inches="tight")
        print("Saved:", png_path, "and", pdf_path)

    plt.show()

def main():
    # Baseline params
    S0, K, r, q, sigma, T = 100.0, 100.0, 0.05, 0.0, 0.20, 1.0
    NS, NA, N, Kgh = 161, 141, 60, 7  # denser grid for smoother frontier

    # Grids
    Sg = s_grid_logspace(S0, sigma, T, k=3.0, NS=NS)
    Ag = a_grid_linear(Sg, NA=NA)

    # Monitoring every step; monthly Bermudan exercise (every 5th step)
    monitor_sched = list(range(1, N+1))
    exercise_sched = [n for n in range(0, N) if (n % 5 == 0 and n > 0)]

    # DP solver for a PUT
    solver_put = DPSolverAsian(Sg, Ag, T=T, N=N, r=r, q=q, sigma=sigma, K=K, is_call=False,
                               K_gh=Kgh, monitor_schedule=monitor_sched,
                               exercise_schedule=exercise_sched)

    price0, masks = solver_put.price(S0=S0, A0=S0, return_frontier=True)
    print(f"Bermudan Asian PUT price (S0=A0=100): {price0:.4f}")

    # Map each returned mask to its exercise step index (chronological)
    ex_steps_sorted = sorted(exercise_sched)            # [5,10,15, ... ,55]
    step_to_idx = {step: i for i, step in enumerate(ex_steps_sorted)}

    targets = [0.25, 0.50, 0.75]
    target_steps = [int(round(frac * N)) for frac in targets]
    target_steps = [s if s in step_to_idx else min(ex_steps_sorted, key=lambda x: abs(x - s))
                    for s in target_steps]

    outdir = "figs"
    os.makedirs(outdir, exist_ok=True)

    for frac, step in zip(targets, target_steps):
        idx = step_to_idx[step]
        mask = masks[idx]
        title = f"Exercise Frontier at t/T ≈ {frac:.2f} (step {step}/{N})"
        savepath = os.path.join(outdir, f"frontier_{int(frac*100):03d}")
        plot_frontier_clean(mask, Sg, Ag, title, savepath=savepath, smooth_sigma=0.4)

if __name__ == "__main__":
    main()