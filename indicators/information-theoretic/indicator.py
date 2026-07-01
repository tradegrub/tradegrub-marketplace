from tg_scripting import *
import numpy as np

indicator("Information Theoretic Indicator", overlay=False)

window = input.int(30, "Window Length", minval=10, maxval=100)
bins = input.int(10, "Histogram Bins", minval=5, maxval=30)
lag = input.int(1, "Transfer Entropy Lag", minval=1, maxval=10)

src = np.array(close, dtype=float)
vol = np.array(volume, dtype=float)
n = len(src)

# Returns
returns = np.zeros(n)
for i in range(1, n):
    if src[i - 1] > 0:
        returns[i] = (src[i] - src[i - 1]) / src[i - 1]

# Volume changes
vol_chg = np.zeros(n)
for i in range(1, n):
    if vol[i - 1] > 0:
        vol_chg[i] = (vol[i] - vol[i - 1]) / vol[i - 1]


def entropy(x, num_bins):
    hist, _ = np.histogram(x, bins=num_bins, density=True)
    hist = hist[hist > 0]
    width = (np.max(x) - np.min(x)) / num_bins if np.max(x) > np.min(x) else 1
    probs = hist * width
    probs = probs[probs > 0]
    return -np.sum(probs * np.log2(probs + 1e-12))


def mutual_info(x, y, num_bins):
    hx = entropy(x, num_bins)
    hy = entropy(y, num_bins)
    # Joint entropy
    hist2d, _, _ = np.histogram2d(x, y, bins=num_bins, density=True)
    hist2d = hist2d[hist2d > 0]
    area = 1.0 / (num_bins * num_bins)
    probs = hist2d * area
    probs = probs[probs > 0]
    hjoint = -np.sum(probs * np.log2(probs + 1e-12))
    return max(hx + hy - hjoint, 0)


def transfer_entropy(source, target, k):
    n_te = len(source) - k
    if n_te < 10:
        return 0.0
    # Discretize
    s_bins = np.digitize(source, np.linspace(np.min(source), np.max(source), bins + 1)[:-1])
    t_bins = np.digitize(target, np.linspace(np.min(target), np.max(target), bins + 1)[:-1])
    # Count transitions
    counts = {}
    for i in range(k, len(source)):
        key = (t_bins[i], t_bins[i - k], s_bins[i - k])
        counts[key] = counts.get(key, 0) + 1
    total = sum(counts.values())
    if total == 0:
        return 0.0
    # Marginal counts
    ct_tp = {}
    ct_tp_sp = {}
    for (t, tp, sp), c in counts.items():
        ct_tp[(t, tp)] = ct_tp.get((t, tp), 0) + c
        ct_tp_sp[(tp, sp)] = ct_tp_sp.get((tp, sp), 0) + c
    ct_tp_only = {}
    for (t, tp), c in ct_tp.items():
        ct_tp_only[tp] = ct_tp_only.get(tp, 0) + c
    te = 0.0
    for (t, tp, sp), c in counts.items():
        p_joint = c / total
        p_t_given_tp_sp = c / max(ct_tp_sp.get((tp, sp), 1), 1)
        p_t_given_tp = ct_tp.get((t, tp), 1) / max(ct_tp_only.get(tp, 1), 1)
        if p_t_given_tp > 0 and p_t_given_tp_sp > 0:
            te += p_joint * np.log2(p_t_given_tp_sp / p_t_given_tp + 1e-12)
    return max(te, 0)


# Rolling computations
mi_series = np.full(n, 0.0)
te_vol_price = np.full(n, 0.0)
self_info = np.full(n, 0.0)

for t in range(window, n):
    r_win = returns[t - window:t]
    v_win = vol_chg[t - window:t]

    if np.std(r_win) > 1e-10 and np.std(v_win) > 1e-10:
        mi_series[t] = mutual_info(r_win, v_win, bins)
        te_vol_price[t] = transfer_entropy(v_win, r_win, lag)

    self_info[t] = entropy(r_win, bins)

# Normalize for display
mi_max = np.nanmax(mi_series)
if mi_max > 0:
    mi_norm = (mi_series / mi_max) * 100
else:
    mi_norm = mi_series

te_max = np.nanmax(te_vol_price)
if te_max > 0:
    te_norm = (te_vol_price / te_max) * 100
else:
    te_norm = te_vol_price

si_max = np.nanmax(self_info)
if si_max > 0:
    si_norm = (self_info / si_max) * 100
else:
    si_norm = self_info

plot(mi_norm.tolist(), title="Mutual Information", color="#42A5F5", linewidth=2)
plot(te_norm.tolist(), title="Transfer Entropy", color="#AB47BC", linewidth=1)
plot(si_norm.tolist(), title="Self Entropy", color="#FFA726", linewidth=1)
hline(50, title="Mid", color="#555", linestyle="dashed")
