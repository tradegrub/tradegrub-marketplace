from tg_scripting import *

rsi_len = input.int(14, "RSI Length", minval=5, maxval=50)
cci_len = input.int(20, "CCI Length", minval=5, maxval=50)
stoch_len = input.int(14, "Stochastic Length", minval=5, maxval=50)
signal_len = input.int(5, "Signal Length", minval=2, maxval=20)

import numpy as np

indicator("Momentum Composite", overlay=False)

rsi_val = ta.rsi(close, rsi_len)
rsi_norm = (rsi_val - 50) / 50

cci_val = ta.cci(close, cci_len)
cci_norm = np.clip(cci_val / 200, -1, 1)

stoch_k, stoch_d = ta.stoch(high, low, close, stoch_len, 3, 3)
stoch_norm = (stoch_k - 50) / 50

composite = (rsi_norm + cci_norm + stoch_norm) / 3 * 100
signal = ta.sma(composite, signal_len)

plot(composite, title="Momentum Composite", color="#7E57C2")
plot(signal, title="Signal", color="#FF8A65")
hline(50, title="Overbought", color="rgba(239,83,80,0.5)")
hline(-50, title="Oversold", color="rgba(38,166,154,0.5)")
hline(0, title="Zero", color="rgba(128,128,128,0.3)")

bgcolor(composite > 50, color="rgba(239,83,80,0.06)")
bgcolor(composite < -50, color="rgba(38,166,154,0.06)")

# --- Rich annotations ---
show_labels = input.bool(True, "Show Labels")
show_levels = input.bool(True, "Show Levels")

cross_up_ob = ta.crossover(composite, 50)
cross_down_os = ta.crossunder(composite, -50)
cross_up_zero = ta.crossover(composite, 0)
cross_down_zero = ta.crossunder(composite, 0)

n = len(close)
last_label_idx = -100
cooldown = 15

for i in range(signal_len, n):
    if not show_labels:
        break
    if (i - last_label_idx) <= cooldown:
        continue

    if cross_up_ob[i]:
        last_label_idx = i
        label.new(
            x=i, y=float(composite[i]),
            text="Overbought",
            style=label.style_label_down,
            color="rgba(239,83,80,0.3)",
            textcolor="#ef5350",
            size="small"
        )
    elif cross_down_os[i]:
        last_label_idx = i
        label.new(
            x=i, y=float(composite[i]),
            text="Oversold",
            style=label.style_label_up,
            color="rgba(38,166,154,0.3)",
            textcolor="#26a69a",
            size="small"
        )
    elif cross_up_zero[i]:
        last_label_idx = i
        label.new(
            x=i, y=float(composite[i]),
            text="Bullish Cross",
            style=label.style_label_up,
            color="rgba(0,230,118,0.3)",
            textcolor="#00e676",
            size="small"
        )
    elif cross_down_zero[i]:
        last_label_idx = i
        label.new(
            x=i, y=float(composite[i]),
            text="Bearish Cross",
            style=label.style_label_down,
            color="rgba(239,83,80,0.3)",
            textcolor="#ef5350",
            size="small"
        )
