from tg_scripting import *
import numpy as np

indicator("Volume Divergence Scanner", overlay=False)

swing_len = input.int(5, "Swing Lookback", minval=2, maxval=20)
min_bars = input.int(10, "Min Bars Between Swings", minval=3, maxval=50)
show_labels = input.bool(True, "Show Labels")

cl = np.array(close, dtype=float)
hi = np.array(high, dtype=float)
lo = np.array(low, dtype=float)
vol = np.array(volume, dtype=float)
n = len(cl)

# --- Find swing highs and swing lows ---

def find_swing_highs(data, length):
    swings = []
    for i in range(length, n - length):
        if data[i] == np.max(data[i - length:i + length + 1]):
            swings.append(i)
    return swings

def find_swing_lows(data, length):
    swings = []
    for i in range(length, n - length):
        if data[i] == np.min(data[i - length:i + length + 1]):
            swings.append(i)
    return swings

price_swing_highs = find_swing_highs(hi, swing_len)
price_swing_lows = find_swing_lows(lo, swing_len)
vol_swing_highs = find_swing_highs(vol, swing_len)
vol_swing_lows = find_swing_lows(vol, swing_len)

# --- Match swing points and detect divergences ---

bull_signal = np.zeros(n, dtype=bool)
bear_signal = np.zeros(n, dtype=bool)
div_strength = np.full(n, np.nan)

def find_nearest_vol_swing(vol_swings, bar_idx, tolerance):
    best = None
    best_dist = tolerance + 1
    for vs in vol_swings:
        dist = abs(vs - bar_idx)
        if dist <= tolerance and dist < best_dist:
            best = vs
            best_dist = dist
    return best

tolerance = swing_len + 2

# Bullish divergence: consecutive price swing lows where price LL, volume HL
for i in range(1, len(price_swing_lows)):
    curr_idx = price_swing_lows[i]
    prev_idx = price_swing_lows[i - 1]
    if curr_idx - prev_idx < min_bars:
        continue
    # Price makes lower low
    if lo[curr_idx] >= lo[prev_idx]:
        continue
    # Find corresponding volume swing lows
    v_curr = find_nearest_vol_swing(vol_swing_lows, curr_idx, tolerance)
    v_prev = find_nearest_vol_swing(vol_swing_lows, prev_idx, tolerance)
    if v_curr is None or v_prev is None:
        continue
    # Volume makes higher low
    if vol[v_curr] > vol[v_prev]:
        bull_signal[curr_idx] = True
        price_range = abs(lo[prev_idx] - lo[curr_idx])
        vol_range = abs(vol[v_curr] - vol[v_prev])
        norm_p = price_range / (lo[prev_idx] + 1e-10)
        norm_v = vol_range / (vol[v_prev] + 1e-10)
        div_strength[curr_idx] = (norm_p + norm_v) / 2 * 100

# Bearish divergence: consecutive price swing highs where price HH, volume LH
for i in range(1, len(price_swing_highs)):
    curr_idx = price_swing_highs[i]
    prev_idx = price_swing_highs[i - 1]
    if curr_idx - prev_idx < min_bars:
        continue
    # Price makes higher high
    if hi[curr_idx] <= hi[prev_idx]:
        continue
    # Find corresponding volume swing highs
    v_curr = find_nearest_vol_swing(vol_swing_highs, curr_idx, tolerance)
    v_prev = find_nearest_vol_swing(vol_swing_highs, prev_idx, tolerance)
    if v_curr is None or v_prev is None:
        continue
    # Volume makes lower high
    if vol[v_curr] < vol[v_prev]:
        bear_signal[curr_idx] = True
        price_range = abs(hi[curr_idx] - hi[prev_idx])
        vol_range = abs(vol[v_prev] - vol[v_curr])
        norm_p = price_range / (hi[prev_idx] + 1e-10)
        norm_v = vol_range / (vol[v_prev] + 1e-10)
        div_strength[curr_idx] = -(norm_p + norm_v) / 2 * 100

# --- Build continuous divergence strength line ---

strength_line = np.zeros(n)
last_val = 0.0
decay = 0.92
for i in range(n):
    if not np.isnan(div_strength[i]):
        last_val = div_strength[i]
    else:
        last_val *= decay
    strength_line[i] = last_val

# --- Plot outputs ---

plot(strength_line.tolist(), title="Divergence Strength", color="#ab47bc", linewidth=2)
hline(0, title="Zero", color="#888888", linestyle="dashed")

bull_bg = np.zeros(n, dtype=bool)
bear_bg = np.zeros(n, dtype=bool)
for i in range(n):
    if bull_signal[i]:
        for j in range(i, min(i + 3, n)):
            bull_bg[j] = True
    if bear_signal[i]:
        for j in range(i, min(i + 3, n)):
            bear_bg[j] = True

bgcolor(bull_bg.tolist(), color="rgba(76,175,80,0.12)")
bgcolor(bear_bg.tolist(), color="rgba(244,67,54,0.12)")

if show_labels:
    for i in range(n):
        if bull_signal[i]:
            label.new(i, strength_line[i], "Bull Div", color="#4CAF50", textcolor="#ffffff", style="label_up", size="tiny")
        if bear_signal[i]:
            label.new(i, strength_line[i], "Bear Div", color="#f44336", textcolor="#ffffff", style="label_down", size="tiny")
