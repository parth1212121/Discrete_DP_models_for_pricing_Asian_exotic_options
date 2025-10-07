
# 🧮 Discrete dynamic programming models for pricing Asian exotic options

This repository implements **discrete dynamic programming (DP)** models for pricing **Asian exotic options** — including **European**, **Bermudan**, and **American** styles.  
It provides validated numerical convergence studies, early-exercise frontier visualizations, early-premium analysis, and full sensitivity overlays.

---

## 📂 Repository Structure

```
.
├── dp_asian.py                 # DP solver engine
├── grids.py                    # Grid construction utilities
├── mc_asian.py                 # Monte Carlo baseline (European Asian)
│
├── convergence_study.py        # DP–MC convergence plots
├── exersize_frontier.py        # Bermudan exercise frontier visualization
├── early_premium.py            # Early-exercise premium vs parameters
├── sensitivity_stats.py        # Overlay sensitivities: Euro vs Berm vs Amer
│
├── figs/                       # Frontier plots (auto-generated)
├── premium_figs/               # Early-premium plots
├── sensitivity_overlay/        # Sensitivity overlay plots
└── convergence_figs/           # Convergence plots
```

---

## ⚙️ 1. Core Mathematical Model

We discretize the **state space** \\((S, A)\\) where:

- Spot price \\(S_t\\) follows a lognormal process:
  $$
  S_{t+\Delta t} = S_t \, e^{(r-q-\frac{1}{2}\sigma^2)\Delta t + \sigma\sqrt{\Delta t}\,Z}
  $$

- Arithmetic average is updated as:
  $$
  A_{t+\Delta t} = \frac{kA_t + S_{t+\Delta t}}{k+1}, \quad \text{if } t \text{ is a monitoring date.}
  $$

- Bellman recursion:
  $$
  V_n(S,A) =
  \begin{cases}
  e^{-r\Delta t}\,\mathbb{E}[\,V_{n+1}(S',A')\,], & \text{(continuation)} \\[4pt]
  \max\{\Phi(S,A),\,e^{-r\Delta t}\,\mathbb{E}[V_{n+1}] \}, & \text{(exercise step)}
  \end{cases}
  $$

Expectation is computed using **Gauss–Hermite quadrature** over the normal random variable \\(Z\\).

---

## 🧩 2. Script Summaries and Usage

### **(a) `convergence_study.py`**
Validates the DP solver against Monte Carlo (European Asian baseline).

**Usage:**
```bash
python convergence_study.py --param NS --values 81,101,121,161,201
```

**Generates:**
- `convergence_NS.png`, `convergence_NA.png`, `convergence_Kgh.png` (in `/convergence_figs/`)
- Each shows **error vs grid parameter** (|DP − MC|)

**Interpretation:**
- Error decreases as discretization refines — proof of convergence.

---

### **(b) `exersize_frontier.py`**
Plots the **Bermudan early-exercise frontier** for an Asian Put.

**Concept:**
At each time slice, we plot the **exercise region** (yellow) and **continuation region** (purple).  
The **white contour** marks the 0.5 level — the precise boundary of early exercise.

**Usage:**
```bash
python exersize_frontier.py
```

**Outputs:**
```
figs/
 ├── frontier_025.png
 ├── frontier_050.png
 └── frontier_075.png
```
Each corresponds to \\(t/T \in \{0.25, 0.5, 0.75\}\\).

**Interpretation:**
- White line = optimal early-exercise boundary.  
- Region above (low A, low S) → exercise; region below → continuation.

---

### **(c) `early_premium.py`**
Computes the **early-exercise premium**:

$$
\text{Premium} = V_{\text{Berm/Am}} - V_{\text{Euro}}
$$

and plots how it changes with parameters \\(M, \sigma, K\\).

**Usage examples:**
```bash
python early_premium.py --do_M --style berm
python early_premium.py --do_sigma --style amer
python early_premium.py --do_K --style berm
```

**Outputs:** `/premium_figs/`
```
premium_vs_M.png
premium_vs_sigma.png
premium_vs_K.png
```

**Interpretation:**
- Premium ↑ with volatility \\(\sigma\\).  
- Premium ↓ with number of monitoring dates \\(M\\) (averaging smooths paths).  
- Premium peaks near-the-money, small when deep ITM or OTM.

---

### **(d) `sensitivity_stats.py`**
Generates **overlay sensitivity plots** comparing European, Bermudan, and American options.

**Usage:**
```bash
python sensitivity_stats.py
```

**Outputs:** `/sensitivity_overlay/`
| File | X-Axis | Description |
|------|--------|-------------|
| `price_vs_sigma.png` | Volatility \\(\\sigma\\) | Price increases with \\(\\sigma\\) |
| `price_vs_r.png` | Interest rate \\(r\\) | Discounting + drift effect |
| `price_vs_K.png` | Strike \\(K\\) | Decreasing function of \\(K\\) |
| `price_vs_M.png` | Time steps \\(M=N\\) | Combined averaging + granularity effect |

**Interpretation:**
$$
V_{Euro} \le V_{Berm} \le V_{Amer}
$$
Overlay plots clearly show the gain in flexibility (exercise value).

---

## 📊 3. Figure Directory Layout

```
figs/
 ├── frontier_025.png
 ├── frontier_050.png
 └── frontier_075.png

premium_figs/
 ├── premium_vs_M.png
 ├── premium_vs_sigma.png
 └── premium_vs_K.png

sensitivity_overlay/
 ├── price_vs_sigma.png
 ├── price_vs_r.png
 ├── price_vs_K.png
 └── price_vs_M.png

convergence_figs/
 ├── convergence_NS.png
 ├── convergence_NA.png
 └── convergence_Kgh.png
```

---

## 📈 4. Typical Observations

| Feature | Observation |
|----------|--------------|
| **Convergence** | DP error stabilizes well within MC 95% CI. |
| **Frontier** | Moves inward with time; smooth transition from early exercise to continuation. |
| **Premium vs σ** | Increases sharply with volatility. |
| **Premium vs M** | Decreases (averaging reduces path variance). |
| **Sensitivity overlays** | Maintain hierarchy Euro < Berm < Amer. |

---

## 📜 5. References

- Rogers & Shi (1995), *The Value of an Asian Option*, J. Appl. Prob.  
- Hull (2020), *Options, Futures, and Other Derivatives*.  
- Carverhill (1992), *Discrete Dynamic Programming for Option Pricing*.

---

### 🧠 Tip
All scripts share a unified solver `DPSolverAsian`, so extending this framework to **barrier** or **lookback** options only requires modifying the payoff function.

---
