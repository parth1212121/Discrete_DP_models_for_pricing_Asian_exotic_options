
# 🧮 Discrete Dynamic Programming Models for Pricing Asian Exotic Options

This repository implements **discrete dynamic programming (DP)** models for pricing **Asian exotic options** — including **European**, **Bermudan**, and **American** styles.  
It provides validated numerical convergence studies, early-exercise frontier visualizations, early-premium analysis, and full sensitivity overlays.

---

## 📂 Repository Structure

```
.
├── cli_dp.py                   # Command-line interface for DP solver
├── cli_mc.py                   # Command-line interface for Monte Carlo solver
│
├── convergence_study.py        # DP–MC convergence validation study
├── dp_asian.py                 # Core dynamic programming solver engine
├── early_premium.py            # Early-exercise premium analysis
├── exersize_frontier.py        # Bermudan exercise frontier visualization
├── gh.py                       # Gauss–Hermite quadrature utilities
├── grids.py                    # Grid construction utilities for S and A
├── interp2d.py                 # Bilinear interpolation routines
├── mc_asian.py                 # Monte Carlo baseline for European Asian options
├── plots.py                    # Common plotting helpers and formatting
│
├── convergence_study.py        # DP–MC convergence plots
├── exersize_frontier.py        # Bermudan exercise frontier visualization
├── early_premium.py            # Early-exercise premium vs parameters
├── sensitivity_stats.py        # Overlay sensitivities: Euro vs Berm vs Amer
│
├── exersize_frontier_figs/     # Frontier plots (auto-generated)
├── premium_figs/               # Early-premium plots
├── sensitivity_figs/           # Sensitivity overlay plots
└── convergence_figs/           # Convergence plots
|
├── README.md                   # Project documentation (this file)
└── requirements.txt            # Python dependencies list
```

---

---

## 🚀 Installation


Clone the repository and install dependencies via `requirements.txt`:

```bash
git clone https://github.com/<your-username>/<repo-name>.git
cd <repo-name>
pip install -r requirements.txt
```



## ⚙️ 1. Core Mathematical Model

We discretize the **state space** \((S, A)\), where:

- **Underlying dynamics:**
  ```math
  S_{t+\Delta t} = S_t \, e^{(r-q-\frac{1}{2}\sigma^2)\Delta t + \sigma\sqrt{\Delta t}\,Z}
  ```

- **Arithmetic average update:**
  ```math
  A_{t+\Delta t} = \frac{kA_t + S_{t+\Delta t}}{k+1}, \quad \text{if } t \text{ is a monitoring date.}
  ```

- **Dynamic programming recursion:**
  ```math
  V_n(S,A) =
  \begin{cases}
  e^{-r\Delta t}\,\mathbb{E}[\,V_{n+1}(S',A')\,], & \text{(continuation)} \\[4pt]
  \max\{\Phi(S,A),\,e^{-r\Delta t}\,\mathbb{E}[V_{n+1}] \}, & \text{(exercise step)}
  \end{cases}
  ```

Expectation E[.] is evaluated using **Gauss–Hermite quadrature** with pre-tabulated nodes and weights.

---

## 🧩 2. Script Summaries and Command-Line Usage

### 🧮 `convergence_study.py` — Numerical Validation

Validates DP solver convergence against Monte Carlo pricing for **European Asian options**.

#### Command-line options
```bash
--param {NS,NA,Kgh}   # which grid parameter to sweep
--values VALS          # comma-separated list of values, e.g. 81,101,121,161,201
--N 60                 # number of time steps (default 60)
--Kgh 7                # number of Gauss–Hermite nodes
--outdir convergence_figs
```
Example:
```bash
python convergence_study.py --param NS --values 81,101,121,161,201,301
```

#### Output
- `convergence_NS.png`, `convergence_NA.png`, `convergence_Kgh.png`
- Each plot shows error |DP − MC| vs parameter.

#### Typical plot
![Convergence on varying Ns](convergence_figs/conv_NS.png)
![Convergence on varying Na](convergence_figs/conv_NA.png)
![Convergence on varying Kgh](convergence_figs/conv_Kgh.png)

#### Interpretation

- **Error vs NS (number of spot grid points):**  
  Increasing the number of \(S\)-grid nodes leads to a clear reduction in pricing error.  
  The DP estimate converges steadily toward the Monte Carlo benchmark, and beyond NS ≈ 200, the error drops below the Monte Carlo confidence interval — confirming spatial grid stability.

- **Error vs NA (number of average grid points):**  
  Refining the \(A\)-grid greatly improves accuracy because the arithmetic-average dimension introduces additional state variability.  
  As NA increases, the DP error decreases rapidly, showing that discretization of the average is the dominant source of bias.

- **Error vs Kgh (number of Gauss–Hermite nodes):**  
  Increasing the quadrature order improves the approximation of the conditional expectation.  
  However, convergence in Kgh is relatively fast — beyond Kgh = 5 nodes, the improvement becomes marginal, indicating that quadrature error is secondary compared to grid discretization.

- **Overall observation:**  
  All three parameters (\(NS\), \(NA\), \(Kgh\)) show **monotonic convergence** of DP prices toward the Monte Carlo reference.  
  The fact that |DP − MC| remains consistently **below the Monte Carlo 95% confidence half-width** validates both the **numerical accuracy** and **stochastic consistency** of the DP solver.

---

### ⚖️ `exersize_frontier.py` — Bermudan Exercise Frontier

Plots the **optimal early-exercise boundary** for a Bermudan Asian put option.

#### Command-line options
```bash
--NS 121        # grid points for S
--NA 101        # grid points for A
--N 60          # time steps
--Kgh 7         # quadrature nodes
--sigma 0.2     # volatility
--K 100         # strike price
--r 0.05        # interest rate
--outdir exersize_frontier_figs   # output directory
```
Example:
```bash
python exersize_frontier.py 
```

#### Output
Three clean frontier plots at different times:

| Plot | Description |
|------|--------------|
| `frontier_025.png` | Frontier at 25% maturity |
| `frontier_050.png` | Frontier at 50% maturity |
| `frontier_075.png` | Frontier at 75% maturity |

#### Typical plot
![Frontier at 25% maturity](exersize_frontier_figs/frontier_025.png)
![Frontier at 50% maturity](exersize_frontier_figs/frontier_050.png)
![Frontier at 75% maturity](exersize_frontier_figs/frontier_075.png)

#### Interpretation

- **Color coding:**  
  Yellow regions correspond to the **exercise region**, where the immediate payoff from exercising exceeds the continuation value.  
  Purple regions denote the **continuation region**, where it is optimal to hold the option and wait for future information.

- **Frontier shape:**  
  The frontier separates these two regions in the (S, A) plane.  
  It slopes **upward**, indicating that for higher arithmetic averages \(A\), a higher spot price \(S\) is required to make immediate exercise optimal.  
  This arises because a larger historical average reduces the additional benefit of waiting for further upward movement in \(S\).

- **Temporal evolution:**  
  As maturity approaches (from 25% → 50% → 75%), the **exercise region expands**, and the continuation region shrinks.  
  This behavior is consistent with the **time-decay effect**: the closer the option is to expiration, the less time value remains, prompting earlier exercise in deep in-the-money regions.

- **Economic intuition:**  
  The observed movement of the boundary illustrates rational early-exercise behavior —  
  holders are more inclined to exercise when (i) the option is deep ITM, and (ii) little time remains to recover potential value from holding.  
  The gradual inward shift of the boundary visually captures this dynamic decision-making process over time.


---

### 💰 `early_premium.py` — Early-Exercise Premium Analysis

Computes and plots the **early-exercise premium**:
```math
\text{Premium} = V_{\text{Berm/Am}} - V_{\text{Euro}}
```

#### Command-line options
```bash
--do_M          # vary number of time steps / monitoring dates
--do_sigma      # vary volatility
--do_K          # vary strike
--style {berm,amer}    # option style
--freq 5        # Bermudan exercise every `freq` steps
--outdir premium_figs
```

Examples:
```bash
python early_premium.py --do_M 
python early_premium.py --do_sigma --style amer
python early_premium.py --do_K --style berm
```

#### Output
| File | Description |
|------|--------------|
| `premium_vs_M.png` | Premium vs number of time steps |
| `premium_vs_sigma.png` | Premium vs volatility |
| `premium_vs_K.png` | Premium vs strike |

#### Typical plots
![Premium vs M](premium_figs/premium_vs_M.png)
![Premium vs Sigma](premium_figs/premium_vs_sigma.png)
![Premium vs K](premium_figs/premium_vs_K.png)

#### Interpretation

- **Meaning of M:**  
  Here, \( M \) represents the **number of discrete timesteps** in the dynamic programming (DP) grid.  
  In this implementation, we set \( M = N \), so **monitoring** (for updating the running average) and **exercise opportunities** (for Bermudan/American cases) occur at **every DP timestep**.  
  Increasing \( M \) therefore means a **finer temporal discretization** — smaller \( \Delta t = T/M \) — providing both more frequent averaging updates and more frequent potential exercises.

- **Premium vs Monitoring Frequency (M):**  
  The early-exercise premium **increases with M** in this configuration.  
  This happens because a higher \( M \) gives the option holder **more flexibility** — the model checks for possible exercise at more time points, bringing the Bermudan price closer to the true American limit.  
  Simultaneously, finer averaging (smaller \(\Delta t\)) improves numerical accuracy and slightly smooths the payoff surface, but the dominant effect comes from the **increased number of decision points** for early exercise.  
  Hence, as \( M \) increases, the Bermudan and American prices rise monotonically toward their continuous-time values, while the European price remains essentially unchanged.

- **Premium vs Volatility (σ):**  
  The premium grows approximately linearly with volatility.  
  As σ increases, the uncertainty in the underlying path grows, enhancing the **optionality** of early exercise.  
  With higher volatility, the continuation value fluctuates more widely, giving the holder greater opportunity to benefit from favorable price movements.  
  Hence, higher σ → larger early-exercise premium.

- **Premium vs Strike (K):**  
  The premium rises sharply as K increases (moving deeper **in-the-money** for a put).  
  When strike is high, the holder gains more from early exercise since the payoff (K − A) becomes significant earlier.  
  For near at-the-money (ATM) strikes, the time value dominates, so early exercise adds limited value.  
  Thus, the premium curve shows a **convex upward shape**, peaking in the ITM region.

- **Overall observation:**  
  Across all parameters, the early-exercise premium behaves consistently with theoretical intuition:  
  it grows with volatility, increases with finer time discretization (more frequent exercise opportunities), and rises with moneyness (higher strike).  
  These results confirm that the dynamic programming solver correctly captures the trade-off between **holding for time value** and **exercising for intrinsic value**.
---

### 📊 `sensitivity_stats.py` — Multi-Style Sensitivity Overlay

Generates **overlay charts** for European, Bermudan, and American Asian options.

#### Command-line options
```bash
--sigmas 0.10,0.20,0.30,0.40,0.50
--rates 0.00,0.02,0.05,0.08
--strikes 80,90,100,110,120
--M_list 12,24,52
--berm_freq 5
--NS 121 --NA 101 --N 60 --Kgh 7
--outdir sensitivity_overlay
```

#### Example
```bash
python sensitivity_stats.py
```

#### Theoretical Hierarchy
For any parameter configuration, the prices maintain the fundamental inequality:

<small>V<sub>Euro</sub> ≤ V<sub>Berm</sub> ≤ V<sub>Amer</sub></small>

This reflects the fact that additional exercise flexibility (more decision points) can never reduce value.


---

#### Parameter-by-Parameter Interpretation

#### **1️⃣ Volatility (σ) — “Optionality driver”**
- **Trend:** Prices **increase almost linearly** with σ for all three styles.  
- **Reason:** Higher volatility raises the uncertainty in future payoffs, which **increases the option’s time value**.  
  Early exercise becomes more valuable since the underlying can deviate further from its mean path, giving the holder more favorable scenarios to lock in profit early.  
- **Hierarchy:** The spread between Bermudan and American widens slightly at high σ — this is where early exercise flexibility is most beneficial.

📈 **Plot:**  
![Price vs Sigma](sensitivity_figs/price_vs_sigma.png)

---

#### **2️⃣ Strike (K) — “Moneyness effect”**
- **Trend:** Prices **increase with K** (for a put).  
- **Reason:** A higher strike increases intrinsic value \( (K - A) \), making early exercise attractive even before maturity.  
  Deep in-the-money (ITM) puts have high exercise probability, while out-of-the-money (OTM) puts are dominated by time value.  
- **Observation:** The three curves remain tightly packed — indicating that the Asian averaging dampens extreme payoff swings compared to plain vanilla options.

📈 **Plot:**  
![Price vs K](sensitivity_figs/price_vs_K.png)

---

#### **3️⃣ Interest Rate (r) — “Discounting vs drift”**
- **Trend:** Prices **decrease with r**.  
- **Reason:** Higher rates increase the risk-free growth of the underlying asset, reducing the likelihood that the option finishes ITM.  
  Moreover, higher discounting reduces the present value of future payoffs.  
- **Observation:** The slopes of all curves are roughly parallel, confirming that early exercise flexibility has limited impact on the rate sensitivity (the discounting factor affects all styles similarly).

📈 **Plot:**  
![Price vs r](sensitivity_figs/price_vs_r.png)

---

#### **4️⃣ Monitoring Frequency (M) — “Averaging granularity”**
- **Trend:** Prices **increase slightly with M** for Bermudan and American options, while the European price tends to stabilize.  
- **Reason:** Increasing M means finer discretization (smaller Δt), offering **more opportunities to exercise** (for Bermudan/American) and **smoother averaging** of the payoff.  
  As M grows, Bermudan prices approach American prices, reflecting convergence toward the continuous-time limit.  
- **Observation:** The small gap between styles shows that averaging smooths volatility effects — the difference between European and American styles is smaller for Asian options than for plain vanilla ones.

📈 **Plot:**  
![Price vs M](sensitivity_figs/price_vs_M.png)

---

#### Summary Table

| Parameter | Trend | Key Effect | Main Beneficiary |
|------------|--------|-------------|------------------|
| **σ (Volatility)** | ↑ | More uncertainty → higher option value | American (max optionality) |
| **K (Strike)** | ↑ (for puts) | Higher intrinsic value | All, esp. ITM |
| **r (Rate)** | ↓ | Discounting & drift reduce payoff | All styles |
| **M (Monitoring)** | ↑ | More frequent exercise & smoother averaging | Bermudan, American |

---

#### Overall Insights

- Dynamic programming captures **the correct monotonic behavior** across all model dimensions.  
- The **gap between styles (Euro < Berm < Amer)** remains stable, validating numerical consistency.  
- Asian averaging **reduces sensitivity** to volatility and rate changes compared to plain vanilla options — a signature characteristic of path-dependent derivatives.

---

## 🧪 3. Reproduction Workflow

1. Run convergence validation:
   ```bash
   python convergence_study.py --param NS --values 81,121,161,201,301
   python convergence_study.py --param NA --values 61,81,101,141,181
   python convergence_study.py --param Kgh --values 3,5,7
   ```
2. Generate Bermudan frontiers:
   ```bash
   python exersize_frontier.py
   ```
3. Compute early-exercise premium curves:
   ```bash
   python early_premium.py --do_M
   python early_premium.py --do_sigma 
   python early_premium.py --do_K 
   ```
4. Produce multi-style overlays:
   ```bash
   python sensitivity_stats.py
   ```

---

## 📜 4. References

- Rogers & Shi (1995), *The Value of an Asian Option*, J. Appl. Prob.  
- Hull (2020), *Options, Futures, and Other Derivatives*.  
- Carverhill (1992), *Discrete Dynamic Programming for Option Pricing*.


