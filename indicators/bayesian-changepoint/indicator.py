from tg_scripting import *
import numpy as np

indicator("Bayesian Change Point Detector", overlay=False)

hazard = input.int(100, "Hazard Rate", minval=10, maxval=500)
threshold = input.float(0.5, "Detection Threshold", minval=0.1, maxval=0.9, step=0.05)

src = np.array(close, dtype=float)
n = len(src)

# Compute returns
returns = np.diff(src, prepend=src[0])

# Online Bayesian Changepoint Detection (simplified)
# Using a normal-gamma conjugate prior
run_length_prob = np.zeros(n)
changepoint_prob = np.zeros(n)

mu0 = 0.0
kappa0 = 1.0
alpha0 = 1.0
beta0 = 1.0

# Track sufficient stats for each run length
max_rl = min(n, 200)
mu_params = np.full(max_rl, mu0)
kappa_params = np.full(max_rl, kappa0)
alpha_params = np.full(max_rl, alpha0)
beta_params = np.full(max_rl, beta0)

R = np.zeros((max_rl, n))
R[0, 0] = 1.0

lam = 1.0 / hazard

for t in range(1, n):
    x = returns[t]

    # Predictive probability under each run length
    pred_probs = np.zeros(min(t + 1, max_rl))
    for r in range(min(t, max_rl)):
        mu_n = mu_params[r]
        kappa_n = kappa_params[r]
        alpha_n = alpha_params[r]
        beta_n = beta_params[r]
        var = beta_n * (kappa_n + 1) / (alpha_n * kappa_n)
        if var > 0:
            pred_probs[r] = np.exp(-0.5 * (x - mu_n) ** 2 / var) / np.sqrt(2 * np.pi * var)
        else:
            pred_probs[r] = 1e-10

    # Growth probabilities
    growth = R[:min(t, max_rl), t - 1] * pred_probs[:min(t, max_rl)] * (1 - lam)

    # Changepoint probability
    cp = np.sum(R[:min(t, max_rl), t - 1] * pred_probs[:min(t, max_rl)] * lam)

    R[:, t] = 0
    if min(t, max_rl - 1) > 0:
        R[1:min(t + 1, max_rl), t] = growth[:min(t, max_rl - 1)]
    R[0, t] = cp

    # Normalize
    total = np.sum(R[:, t])
    if total > 0:
        R[:, t] /= total

    changepoint_prob[t] = R[0, t]

    # Update parameters for continuing runs
    new_mu = np.full(max_rl, mu0)
    new_kappa = np.full(max_rl, kappa0)
    new_alpha = np.full(max_rl, alpha0)
    new_beta = np.full(max_rl, beta0)
    for r in range(1, min(t + 1, max_rl)):
        k = kappa_params[r - 1]
        m = mu_params[r - 1]
        new_mu[r] = (k * m + x) / (k + 1)
        new_kappa[r] = k + 1
        new_alpha[r] = alpha_params[r - 1] + 0.5
        new_beta[r] = beta_params[r - 1] + 0.5 * k * (x - m) ** 2 / (k + 1)
    mu_params = new_mu
    kappa_params = new_kappa
    alpha_params = new_alpha
    beta_params = new_beta

# Smooth changepoint probability
kern = np.ones(3) / 3
cp_smooth = np.convolve(changepoint_prob, kern, mode='same')
cp_pct = cp_smooth * 100

# Detect changepoints
detected = np.array([cp_smooth[i] > threshold for i in range(n)])

plot(cp_pct.tolist(), title="Change Point Probability", color="#EF5350", linewidth=2)
hline(threshold * 100, title="Threshold", color="#FFA726", linestyle="dashed")
plotshape(detected, title="Change Point", style="triangleup", location="bottom", color="#EF5350")
