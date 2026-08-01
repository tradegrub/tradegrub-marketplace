from tg_scripting import *
import numpy as np

indicator("Recurrence Quantification Analysis", overlay=False)

embed_dim = input.int(3, "Embedding Dimension", minval=2, maxval=5)
delay = input.int(1, "Time Delay", minval=1, maxval=10)
threshold_pct = input.float(10.0, "Threshold (%)", minval=1.0, maxval=50.0, step=1.0)
window = input.int(50, "Rolling Window", minval=20, maxval=100)

src = np.array(close, dtype=float)
n = len(src)

# Compute RQA metrics over rolling windows
recurrence_rate = np.full(n, 50.0)
determinism = np.full(n, 50.0)
entropy_rqa = np.full(n, 50.0)

for t in range(window + embed_dim * delay, n):
    segment = src[t - window:t]
    seg_len = len(segment)

    # Phase space embedding
    m = seg_len - (embed_dim - 1) * delay
    if m < 5:
        continue
    embedded = np.zeros((m, embed_dim))
    for d in range(embed_dim):
        embedded[:, d] = segment[d * delay:d * delay + m]

    # Distance matrix (using max norm)
    eps = threshold_pct / 100.0 * (np.max(segment) - np.min(segment))
    if eps < 1e-10:
        eps = 1e-10

    recur_count = 0
    diag_lengths = []
    total_pairs = 0

    for i in range(m):
        diag_len = 0
        for j in range(i + 1, m):
            dist = np.max(np.abs(embedded[i] - embedded[j]))
            total_pairs += 1
            if dist < eps:
                recur_count += 1
                diag_len += 1
            else:
                if diag_len > 1:
                    diag_lengths.append(diag_len)
                diag_len = 0
        if diag_len > 1:
            diag_lengths.append(diag_len)

    # Recurrence rate
    if total_pairs > 0:
        recurrence_rate[t] = (recur_count / total_pairs) * 100

    # Determinism
    if recur_count > 0 and len(diag_lengths) > 0:
        det_points = sum(diag_lengths)
        determinism[t] = min((det_points / max(recur_count, 1)) * 100, 100)

    # Entropy of diagonal line lengths
    if len(diag_lengths) > 1:
        counts = {}
        for dl in diag_lengths:
            counts[dl] = counts.get(dl, 0) + 1
        total = sum(counts.values())
        ent = 0.0
        for c in counts.values():
            p = c / total
            if p > 0:
                ent -= p * np.log2(p)
        entropy_rqa[t] = ent * 20  # scale for display

# Smooth outputs
kern = np.ones(5) / 5
rr_smooth = np.convolve(recurrence_rate, kern, mode='same')
det_smooth = np.convolve(determinism, kern, mode='same')

plot(rr_smooth.tolist(), title="Recurrence Rate", color="#42A5F5", linewidth=2)
plot(det_smooth.tolist(), title="Determinism", color="#4CAF50", linewidth=1)
plot(entropy_rqa.tolist(), title="Complexity", color="#FFA726", linewidth=1)
hline(50, title="Mid", color="#555", linestyle="dashed")
