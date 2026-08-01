from tg_scripting import *
import numpy as np

indicator("Markov Regime Oscillator", overlay=False)

lookback = input.int(50, "Lookback", minval=20, maxval=200)

src = np.array(close, dtype=float)
n = len(src)

returns = np.abs(np.diff(np.log(src), prepend=0.0))

prob_tt = np.zeros(n)  # P(trend -> trend)
prob_rr = np.zeros(n)  # P(range -> range)
regime_prob = np.zeros(n)  # current regime probability (trending)

for i in range(lookback, n):
    window = returns[i - lookback + 1:i + 1]
    median_ret = float(np.median(window))

    # Classify each bar: 1 = trending, 0 = ranging
    states = (window > median_ret).astype(int)

    # Count transitions
    n_tt = 0  # trend -> trend
    n_tr = 0  # trend -> range
    n_rt = 0  # range -> trend
    n_rr = 0  # range -> range

    for j in range(1, len(states)):
        s_prev = int(states[j - 1])
        s_curr = int(states[j])
        if s_prev == 1 and s_curr == 1:
            n_tt += 1
        elif s_prev == 1 and s_curr == 0:
            n_tr += 1
        elif s_prev == 0 and s_curr == 1:
            n_rt += 1
        else:
            n_rr += 1

    # Transition probabilities
    total_from_t = n_tt + n_tr
    total_from_r = n_rr + n_rt

    prob_tt[i] = (n_tt / total_from_t * 100.0) if total_from_t > 0 else 50.0
    prob_rr[i] = (n_rr / total_from_r * 100.0) if total_from_r > 0 else 50.0

    # Current regime: probability of being in trending state
    # Based on last few bars
    recent = states[-5:]
    regime_prob[i] = float(np.mean(recent)) * 100.0

plot(prob_tt.tolist(), title="P(Trend Persists)", color="#4CAF50", linewidth=2)
plot(prob_rr.tolist(), title="P(Range Persists)", color="#42A5F5", linewidth=2)
plot(regime_prob.tolist(), title="Trend Probability", color="#FFA726", linewidth=1)
hline(50, title="50% Level", color="#666666", linestyle="dashed")
