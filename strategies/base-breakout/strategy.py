from tg_scripting import *
import numpy as np

indicator("Base Breakout", overlay=True)

base_len = input.int(20, "Base Length", minval=10, maxval=60)
range_pct = input.float(5.0, "Max Range %", minval=1.0, maxval=15.0)
vol_mult = input.float(1.5, "Volume Multiplier", minval=1.0, maxval=4.0)
atr_stop = input.float(2.0, "ATR Stop Multiple", minval=0.5, maxval=5.0)
atr_len = input.int(14, "ATR Length", minval=5, maxval=50)
use_ema_filter = input.bool(True, "EMA Trend Filter")
ema_len = input.int(50, "EMA Length", minval=10, maxval=200)
show_labels = input.bool(True, "Show Labels")
show_levels = input.bool(True, "Show Entry/Stop/TP Levels")

base_high = ta.highest(high, base_len)
base_low = ta.lowest(low, base_len)
base_range = (base_high - base_low) / base_low * 100
avg_vol = ta.sma(volume, base_len)
atr = ta.atr(high, low, close, atr_len)
ema_val = ta.ema(close, ema_len)

is_flat = base_range < range_pct
breakout = close > base_high
vol_surge = volume > avg_vol * vol_mult
above_ema = close > ema_val if use_ema_filter else np.ones(len(close), dtype=bool)

entry_signal = is_flat & breakout & vol_surge & above_ema

plot(base_high, title="Base High", color="gray", linewidth=1)
plot(base_low, title="Base Low", color="gray", linewidth=1)
plot(ema_val, title="EMA Filter", color="blue", linewidth=1)
bgcolor(is_flat, color="rgba(100,149,237,0.08)")
plotshape(entry_signal, title="Breakout", shape="triangleup", location="belowbar", color="green")

n = len(close)
last_signal_idx = -100
cooldown = 20
exit_bars = 30
base_label_placed = False

for i in range(len(close)):
    if entry_signal[i]:
        strategy.entry("Long", strategy.LONG)
        strategy.exit("Long", stop=close[i] - atr[i] * atr_stop,
                       limit=close[i] + atr[i] * atr_stop * 2)

        if (i - last_signal_idx) > cooldown:
            last_signal_idx = i
            if show_labels:
                label.new(x=i, y=float(low[i]), text="BREAKOUT",
                          style=label.style_label_up, color="#00e676",
                          textcolor="#000000", size="normal")
                if vol_surge[i]:
                    label.new(x=i, y=float(low[i] - atr[i] * 0.5), text="Vol Surge",
                              style=label.style_none, color="rgba(0,0,0,0)",
                              textcolor="#42a5f5", size="small")
            if show_levels:
                entry_price = float(close[i])
                sl_price = float(close[i] - atr[i] * atr_stop)
                tp_price = float(close[i] + atr[i] * atr_stop * 2)
                end_bar = min(i + exit_bars, n - 1)
                line.new(x1=i, y1=entry_price, x2=end_bar, y2=entry_price,
                         color="#42a5f5", width=1, style=line.style_dashed)
                label.new(x=i + 2, y=entry_price, text="Entry",
                          style=label.style_label_left, color="rgba(66,165,245,0.2)",
                          textcolor="#42a5f5", size="small")
                line.new(x1=i, y1=sl_price, x2=end_bar, y2=sl_price,
                         color="#ef5350", width=1, style=line.style_dashed)
                label.new(x=i + 2, y=sl_price, text="Stop Loss",
                          style=label.style_label_left, color="rgba(239,83,80,0.2)",
                          textcolor="#ef5350", size="small")
                line.new(x1=i, y1=tp_price, x2=end_bar, y2=tp_price,
                         color="#00e676", width=1, style=line.style_dashed)
                label.new(x=i + 2, y=tp_price, text="Take Profit (2:1)",
                          style=label.style_label_left, color="rgba(0,230,118,0.2)",
                          textcolor="#00e676", size="small")
                box.new(left=i, top=tp_price, right=end_bar, bottom=sl_price,
                        border_color="rgba(66,165,245,0.15)", bgcolor="rgba(66,165,245,0.03)")

    # Label the flat base zone once
    if show_labels and not base_label_placed and is_flat[i] and i > base_len:
        base_label_placed = True
        label.new(x=i, y=float(base_high[i]), text="Flat Base",
                  style=label.style_label_down, color="rgba(100,149,237,0.3)",
                  textcolor="#6495ed", size="normal")
