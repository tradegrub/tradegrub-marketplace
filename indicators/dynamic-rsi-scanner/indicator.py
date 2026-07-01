from tg_scripting import *
import numpy as np

indicator("Dynamic RSI Scanner", overlay=False)

# Inputs
base_period = input.int(14, "Base RSI Period", minval=5, maxval=50)
atr_len = input.int(14, "ATR Length", minval=5, maxval=50)
vol_fast = input.int(10, "Volatility Fast MA", minval=3, maxval=30)
vol_slow = input.int(40, "Volatility Slow MA", minval=20, maxval=100)
ob_level = input.int(70, "Overbought Level", minval=60, maxval=90)
os_level = input.int(30, "Oversold Level", minval=10, maxval=40)
div_lookback = input.int(20, "Divergence Lookback", minval=10, maxval=50)
show_labels = input.int(1, "Show Labels (1=Yes)", minval=0, maxval=1)

# ATR-based volatility ratio to adapt RSI period
atr_raw = np.array(ta.atr(high, low, close, atr_len), dtype=float)
atr_raw = np.nan_to_num(atr_raw, nan=0.0)
atr_fast = np.array(ta.sma(atr_raw.tolist(), vol_fast), dtype=float)
atr_slow = np.array(ta.sma(atr_raw.tolist(), vol_slow), dtype=float)
atr_fast = np.nan_to_num(atr_fast, nan=1.0)
atr_slow = np.nan_to_num(atr_slow, nan=1.0)

# Volatility ratio: >1 means expanding vol, <1 contracting
vol_ratio = np.where(atr_slow > 0, atr_fast / atr_slow, 1.0)

# Adaptive period: shorter in high vol, longer in low vol
adaptive_period = np.clip(base_period / vol_ratio, 7, 40).astype(int)

# Compute RSI for several periods and blend based on adaptive period
rsi_short = np.array(ta.rsi(close, 7), dtype=float)
rsi_mid = np.array(ta.rsi(close, 14), dtype=float)
rsi_long = np.array(ta.rsi(close, 28), dtype=float)
rsi_short = np.nan_to_num(rsi_short, nan=50.0)
rsi_mid = np.nan_to_num(rsi_mid, nan=50.0)
rsi_long = np.nan_to_num(rsi_long, nan=50.0)

# Blend weights based on adaptive period
w_short = np.clip(1.0 - (adaptive_period - 7) / 21.0, 0, 1)
w_long = np.clip((adaptive_period - 14) / 14.0, 0, 1)
w_mid = 1.0 - w_short - w_long
w_mid = np.clip(w_mid, 0, 1)
total_w = w_short + w_mid + w_long
w_short /= total_w
w_mid /= total_w
w_long /= total_w

adaptive_rsi = w_short * rsi_short + w_mid * rsi_mid + w_long * rsi_long

# Multi-zone scoring: -2 to +2
zone_score = np.zeros(len(adaptive_rsi))
zone_score = np.where(adaptive_rsi > ob_level + 10, 2.0, zone_score)
zone_score = np.where((adaptive_rsi > ob_level) & (adaptive_rsi <= ob_level + 10), 1.0, zone_score)
zone_score = np.where((adaptive_rsi >= os_level) & (adaptive_rsi <= ob_level), 0.0, zone_score)
zone_score = np.where((adaptive_rsi < os_level) & (adaptive_rsi >= os_level - 10), -1.0, zone_score)
zone_score = np.where(adaptive_rsi < os_level - 10, -2.0, zone_score)

# Smoothed RSI for signal line
rsi_signal = np.array(ta.ema(adaptive_rsi.tolist(), 9), dtype=float)
rsi_signal = np.nan_to_num(rsi_signal, nan=50.0)

# Divergence detection
close_arr = np.array(close, dtype=float)
close_arr = np.nan_to_num(close_arr, nan=0.0)
bull_div = np.full(len(adaptive_rsi), False)
bear_div = np.full(len(adaptive_rsi), False)

for i in range(div_lookback, len(adaptive_rsi)):
    price_window = close_arr[i - div_lookback:i + 1]
    rsi_window = adaptive_rsi[i - div_lookback:i + 1]
    if len(price_window) < 2:
        continue
    price_min_idx = np.argmin(price_window)
    price_max_idx = np.argmax(price_window)
    # Bullish: price makes lower low but RSI makes higher low
    if price_min_idx > 0 and price_window[-1] <= price_window[price_min_idx] and rsi_window[-1] > rsi_window[price_min_idx]:
        if adaptive_rsi[i] < os_level:
            bull_div[i] = True
    # Bearish: price makes higher high but RSI makes lower high
    if price_max_idx > 0 and price_window[-1] >= price_window[price_max_idx] and rsi_window[-1] < rsi_window[price_max_idx]:
        if adaptive_rsi[i] > ob_level:
            bear_div[i] = True

# Overbought/oversold background zones
ob_zone = (adaptive_rsi > ob_level).tolist()
os_zone = (adaptive_rsi < os_level).tolist()

# Plotting
plot(adaptive_rsi.tolist(), title="Adaptive RSI", color="#2196F3", linewidth=2)
plot(rsi_signal.tolist(), title="Signal Line", color="#FF9800", linewidth=1)
plot(zone_score.tolist(), title="Zone Score", color="#9C27B0", linewidth=1)

hline(ob_level, title="Overbought", color="#EF5350", linestyle="dashed")
hline(os_level, title="Oversold", color="#66BB6A", linestyle="dashed")
hline(50, title="Midline", color="#555555", linestyle="dashed")

bgcolor(ob_zone, color="rgba(239,83,80,0.08)")
bgcolor(os_zone, color="rgba(102,187,106,0.08)")

# Divergence labels
if show_labels == 1:
    bar_idx_arr = list(range(len(adaptive_rsi)))
    for i in range(len(adaptive_rsi)):
        if bull_div[i]:
            label.new(x=bar_idx_arr[i], y=adaptive_rsi[i] - 5, text="Bull Div",
                       style=label.style_label_up, color="#4CAF50", textcolor="#FFFFFF", size="small")
        if bear_div[i]:
            label.new(x=bar_idx_arr[i], y=adaptive_rsi[i] + 5, text="Bear Div",
                       style=label.style_label_down, color="#F44336", textcolor="#FFFFFF", size="small")

# Crossover shapes
rsi_list = adaptive_rsi.tolist()
sig_list = rsi_signal.tolist()
cross_up = [rsi_list[i] > sig_list[i] and rsi_list[i - 1] <= sig_list[i - 1] if i > 0 else False for i in range(len(rsi_list))]
cross_dn = [rsi_list[i] < sig_list[i] and rsi_list[i - 1] >= sig_list[i - 1] if i > 0 else False for i in range(len(rsi_list))]

plotshape(cross_up, title="Signal Cross Up", style="triangleup", location="belowbar", color="#4CAF50", size="small")
plotshape(cross_dn, title="Signal Cross Down", style="triangledown", location="abovebar", color="#F44336", size="small")
