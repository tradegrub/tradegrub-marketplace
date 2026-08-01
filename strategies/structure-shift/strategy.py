from tg_scripting import *
import numpy as np

indicator("Structure Shift", overlay=True)

swing_len = input.int(5, "Swing Length", minval=2, maxval=20)
atr_len = input.int(14, "ATR Length", minval=5, maxval=50)
atr_mult = input.float(1.5, "ATR SL Multiplier", minval=0.5, maxval=5.0)
tp_mult = input.float(2.0, "TP Multiplier", minval=1.0, maxval=6.0)
use_choch_only = input.bool(False, "CHoCH Entries Only")
show_levels = input.bool(True, "Show Swing Levels")
show_labels = input.bool(True, "Show Labels")
show_entry_levels = input.bool(True, "Show Entry/Stop/TP Levels")

atr = ta.atr(high, low, close, atr_len)
swing_high = ta.highest(high, swing_len)
swing_low = ta.lowest(low, swing_len)

prev_hh = np.full(len(close), np.nan)
prev_ll = np.full(len(close), np.nan)
trend = np.zeros(len(close))
bos_bull = np.zeros(len(close), dtype=bool)
bos_bear = np.zeros(len(close), dtype=bool)
choch_bull = np.zeros(len(close), dtype=bool)
choch_bear = np.zeros(len(close), dtype=bool)

last_sh = high[0]
last_sl = low[0]
cur_trend = 0

for i in range(swing_len, len(close)):
    if high[i] == swing_high[i] and high[i] > last_sh:
        if cur_trend == -1:
            choch_bull[i] = True
        elif cur_trend == 1:
            bos_bull[i] = True
        last_sh = high[i]
        cur_trend = 1

    if low[i] == swing_low[i] and low[i] < last_sl:
        if cur_trend == 1:
            choch_bear[i] = True
        elif cur_trend == -1:
            bos_bear[i] = True
        last_sl = low[i]
        cur_trend = -1

    prev_hh[i] = last_sh
    prev_ll[i] = last_sl
    trend[i] = cur_trend

for i in range(swing_len, len(close)):
    strategy.set_bar_index(i)
    bull_signal = choch_bull[i] if use_choch_only else (bos_bull[i] | choch_bull[i])
    bear_signal = choch_bear[i] if use_choch_only else (bos_bear[i] | choch_bear[i])

    if bull_signal:
        strategy.entry("Long", strategy.LONG)
        strategy.close("Short")
    if bear_signal:
        strategy.entry("Short", strategy.SHORT)
        strategy.close("Long")

if show_levels:
    plot(prev_hh, title="Swing High", color="green")
    plot(prev_ll, title="Swing Low", color="red")

plotshape(bos_bull, title="BOS Up", shape="triangleup", location="belowbar", color="green")
plotshape(bos_bear, title="BOS Down", shape="triangledown", location="abovebar", color="red")
plotshape(choch_bull, title="CHoCH Up", shape="diamond", location="belowbar", color="lime")
plotshape(choch_bear, title="CHoCH Down", shape="diamond", location="abovebar", color="orange")

# Structure zone background: green tint while in uptrend, red tint while in downtrend
_bg_n = len(close)
bg_colors = [
    ("rgba(38,166,154,0.08)" if trend[i] > 0 else ("rgba(239,83,80,0.08)" if trend[i] < 0 else None))
    for i in range(_bg_n)
]
bgcolor(bg_colors, title="Structure Trend Zone")

# --- Rich annotations ---
n = len(close)
last_signal_idx = -100
cooldown = swing_len * 3
exit_bars = 20

for i in range(swing_len, n):
    bull_signal = choch_bull[i] if use_choch_only else (bos_bull[i] | choch_bull[i])
    bear_signal = choch_bear[i] if use_choch_only else (bos_bear[i] | choch_bear[i])

    if bull_signal and (i - last_signal_idx) > cooldown:
        last_signal_idx = i
        sig_type = "CHoCH" if choch_bull[i] else "BOS"
        if show_labels:
            label.new(x=i, y=float(low[i]), text=sig_type + "\nLONG",
                      style=label.style_label_up, color="#00e676",
                      textcolor="#000000", size="normal")
        if show_entry_levels:
            entry_price = float(close[i])
            sl_price = float(close[i] - atr[i] * atr_mult)
            tp_price = float(close[i] + atr[i] * atr_mult * tp_mult)
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
            label.new(x=i + 2, y=tp_price, text="Take Profit",
                      style=label.style_label_left, color="rgba(0,230,118,0.2)",
                      textcolor="#00e676", size="small")
            box.new(left=i, top=tp_price, right=end_bar, bottom=sl_price,
                    border_color="rgba(66,165,245,0.15)", bgcolor="rgba(66,165,245,0.03)")

    elif bear_signal and (i - last_signal_idx) > cooldown:
        last_signal_idx = i
        sig_type = "CHoCH" if choch_bear[i] else "BOS"
        if show_labels:
            label.new(x=i, y=float(high[i]), text=sig_type + "\nSHORT",
                      style=label.style_label_down, color="#ef5350",
                      textcolor="#ffffff", size="normal")
        if show_entry_levels:
            entry_price = float(close[i])
            sl_price = float(close[i] + atr[i] * atr_mult)
            tp_price = float(close[i] - atr[i] * atr_mult * tp_mult)
            end_bar = min(i + exit_bars, n - 1)
            line.new(x1=i, y1=entry_price, x2=end_bar, y2=entry_price,
                     color="#42a5f5", width=1, style=line.style_dashed)
            line.new(x1=i, y1=sl_price, x2=end_bar, y2=sl_price,
                     color="#ef5350", width=1, style=line.style_dashed)
            label.new(x=i + 2, y=sl_price, text="Stop Loss",
                      style=label.style_label_left, color="rgba(239,83,80,0.2)",
                      textcolor="#ef5350", size="small")
            line.new(x1=i, y1=tp_price, x2=end_bar, y2=tp_price,
                     color="#00e676", width=1, style=line.style_dashed)
            label.new(x=i + 2, y=tp_price, text="Take Profit",
                      style=label.style_label_left, color="rgba(0,230,118,0.2)",
                      textcolor="#00e676", size="small")
            box.new(left=i, top=sl_price, right=end_bar, bottom=tp_price,
                    border_color="rgba(66,165,245,0.15)", bgcolor="rgba(66,165,245,0.03)")
