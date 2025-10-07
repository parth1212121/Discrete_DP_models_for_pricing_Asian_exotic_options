import numpy as np
import matplotlib.pyplot as plt

def plot_frontier(mask, S_grid, A_grid, title='Exercise Frontier'):
    plt.figure()
    plt.imshow(mask.T, origin='lower', aspect='auto',
               extent=[S_grid[0], S_grid[-1], A_grid[0], A_grid[-1]])
    plt.colorbar(label='Exercise (1) / Continue (0)')
    plt.xlabel('S'); plt.ylabel('A'); plt.title(title); plt.tight_layout()
def plot_dp_vs_mc(dp_prices, mc_means, mc_ci_halfwidths, M_list):
    plt.figure()
    xs = np.arange(len(M_list))
    plt.errorbar(xs, mc_means, yerr=mc_ci_halfwidths, fmt='o', label='MC (95% CI)')
    plt.scatter(xs, dp_prices, label='DP', marker='x')
    plt.xticks(xs, [str(m) for m in M_list])
    plt.xlabel('Monitoring dates M'); plt.ylabel('Price')
    plt.title('DP vs MC for European Asian'); plt.legend(); plt.tight_layout()
