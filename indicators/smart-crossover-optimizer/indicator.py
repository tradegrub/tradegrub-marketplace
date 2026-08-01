from tg_scripting import *
import numpy as np
from scipy.optimize import minimize_scalar

indicator("Smart Crossover Optimizer", overlay=True)

# Inputs
train_window = input.int(100, "Training Window", minval=30, maxval=500)
min_fast = input.int(5, "Min Fast Period", minval=2, maxval=20)
max_fast = input.int(30, "Max Fast Period", minval=10, maxval=50)
min_slow = input.int(20, "Min Slow Period", minval=10, maxval=50)
max_slow = input.int(100, "Max Slow Period", minval=30, maxval=200)
reoptimize_every = input.int(20, "Re-optimize Every N Bars", minval=5, maxval=100)
atr_mult = input.int(2, "ATR Filter Multiplier", minval=1, maxval=5)
atr_len = input.int(14, "ATR Length", minval=5, maxval=50)

# Core data
close_arr = np.array(close, dtype=float)
high_arr = np.array(high, dtype=float)
low_arr = np.array(low, dtype=float)
n = len(close_arr)

atr_raw = np.array(ta.atr(high, low, close, atr_len), dtype=float)
atr_vals = np.nan_to_num(atr_raw, nan=0.0)


def rolling_sma(src, length):
    """Compute SMA using numpy cumsum for speed."""
    cs = np.cumsum(src)
    cs[length:] = cs[length:] - cs[:-length]
    result = np.full_like(src, np.nan)
    result[length - 1:] = cs[length - 1:] / length
    return result


def crossover_return(fast_p, slow_p, segment):
    """Evaluate total return of a crossover strategy on a segment."""
    fast_p = int(round(fast_p))
    slow_p = int(round(slow_p))
    if fast_p >= slow_p or slow_p >= len(segment):
        return 0.0
    fast_ma = rolling_sma(segment, fast_p)
    slow_ma = rolling_sma(segment, slow_p)
    position = 0.0
    total_ret = 0.0
    for i in range(slow_p, len(segment)):
        if np.isnan(fast_ma[i]) or np.isnan(slow_ma[i]):
            continue
        if fast_ma[i] > slow_ma[i] and position <= 0:
            position = 1.0
        elif fast_ma[i] < slow_ma[i] and position >= 0:
            position = -1.0
        if i > slow_p:
            total_ret += position * (segment[i] - segment[i - 1]) / segment[i - 1]
    return total_ret


def optimize_periods(segment):
    """Find optimal fast/slow periods via grid + scipy refinement."""
    best_ret = -np.inf
    best_fast, best_slow = min_fast, max_slow
    # Coarse grid search
    for fp in range(min_fast, max_fast + 1, 3):
        for sp in range(max(fp + 5, min_slow), max_slow + 1, 5):
            ret = crossover_return(fp, sp, segment)
            if ret > best_ret:
                best_ret = ret
                best_fast, best_slow = fp, sp
    # Refine fast period with scipy
    def neg_ret_fast(fp):
        return -crossover_return(fp, best_slow, segment)
    res = minimize_scalar(neg_ret_fast, bounds=(min_fast, max_fast), method="bounded")
    best_fast = int(round(res.x))
    # Refine slow period
    def neg_ret_slow(sp):
        return -crossover_return(best_fast, sp, segment)
    res = minimize_scalar(neg_ret_slow, bounds=(max(best_fast + 3, min_slow), max_slow), method="bounded")
    best_slow = int(round(res.x))
    return best_fast, best_slow


# Walk-forward optimization
opt_fast = np.full(n, np.nan)
opt_slow = np.full(n, np.nan)
cur_fast, cur_slow = 10, 50

for i in range(train_window, n):
    if (i - train_window) % reoptimize_every == 0:
        segment = close_arr[i - train_window:i]
        cur_fast, cur_slow = optimize_periods(segment)
    opt_fast[i] = cur_fast
    opt_slow[i] = cur_slow

# Compute adaptive MAs using optimized periods
fast_line = np.full(n, np.nan)
slow_line = np.full(n, np.nan)
for i in range(train_window, n):
    fp = int(opt_fast[i])
    sp = int(opt_slow[i])
    if i >= sp:
        fast_line[i] = np.mean(close_arr[i - fp + 1:i + 1])
        slow_line[i] = np.mean(close_arr[i - sp + 1:i + 1])

# Signals
bullish = [False] * n
bearish = [False] * n
trend_up = [False] * n
for i in range(1, n):
    if np.isnan(fast_line[i]) or np.isnan(slow_line[i]):
        continue
    if np.isnan(fast_line[i - 1]) or np.isnan(slow_line[i - 1]):
        continue
    crossed_up = fast_line[i] > slow_line[i] and fast_line[i - 1] <= slow_line[i - 1]
    crossed_down = fast_line[i] < slow_line[i] and fast_line[i - 1] >= slow_line[i - 1]
    vol_ok = abs(fast_line[i] - slow_line[i]) > atr_vals[i] * atr_mult * 0.1
    if crossed_up and vol_ok:
        bullish[i] = True
    if crossed_down and vol_ok:
        bearish[i] = True
    trend_up[i] = fast_line[i] > slow_line[i]

# Plots
plot(list(fast_line), title="Opt Fast MA", color="#4CAF50", linewidth=2)
plot(list(slow_line), title="Opt Slow MA", color="#FF5252", linewidth=2)

# Background for trend

# Labels on crossover signals
for i in range(n):
    if bullish[i]:
        label.new(x=i, y=low_arr[i], text="BUY", style=label.style_label_up, color="#4CAF50", textcolor="#FFFFFF", size="small")
    if bearish[i]:
        label.new(x=i, y=high_arr[i], text="SELL", style=label.style_label_down, color="#FF5252", textcolor="#FFFFFF", size="small")

# Shapes for additional visual cues
plotshape(bullish, title="Bull Cross", style="triangleup", location="belowbar", color="#4CAF50", size="small")
plotshape(bearish, title="Bear Cross", style="triangledown", location="abovebar", color="#FF5252", size="small")

# Reference lines
hline(0, title="Zero", color="#555555", linestyle="dashed")
