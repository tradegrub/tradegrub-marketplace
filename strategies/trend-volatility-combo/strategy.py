from tg_scripting import *
import numpy as np

indicator("Trend Volatility Combo", overlay=True)

# Inputs
st_len = input.int(10, "Supertrend Length", minval=5, maxval=50)
st_mult = input.float(3.0, "Supertrend Multiplier", minval=1.0, maxval=6.0)
atr_len = input.int(14, "ATR Length", minval=2, maxval=50)
atr_mult = input.float(1.5, "ATR Stop Multiplier", minval=0.5, maxval=5.0)
vol_avg_len = input.int(20, "Volume Average Length", minval=5, maxval=50)
vol_thresh = input.float(1.2, "Volume Threshold", minval=1.0, maxval=5.0)
show_labels = input.bool(True, "Show Labels")
show_levels = input.bool(True, "Show Entry/Stop/TP Levels")

# Calculations
supertrend, supertrend_dir = ta.supertrend(high, low, close, st_len, st_mult)
atr = ta.atr(high, low, close, atr_len)
vol_avg = ta.sma(volume, vol_avg_len)

# Supertrend direction: price above supertrend = bullish
st_bullish = close > supertrend
st_bearish = close < supertrend

# Volume filter
vol_confirmed = volume > (vol_avg * vol_thresh)

# Detect supertrend flips
prev_bullish = np.roll(st_bullish, 1)
prev_bullish[0] = False
prev_bearish = np.roll(st_bearish, 1)
prev_bearish[0] = False

st_flip_bull = st_bullish & prev_bearish
st_flip_bear = st_bearish & prev_bullish

# Entry on supertrend flip with volume confirmation
long_cond = st_flip_bull & vol_confirmed
short_cond = st_flip_bear & vol_confirmed

n = len(close)
last_signal_idx = -100

for i in range(len(close)):
    strategy.set_bar_index(i)
    if long_cond[i]:
        strategy.entry("Long", strategy.LONG)
        strategy.exit("Long SL", from_entry="Long", stop=close[i] - atr[i] * atr_mult)
    elif short_cond[i]:
        strategy.entry("Short", strategy.SHORT)
        strategy.exit("Short SL", from_entry="Short", stop=close[i] + atr[i] * atr_mult)

    # --- Rich annotations ---
    if long_cond[i] and (i - last_signal_idx) > 20:
        last_signal_idx = i
        if show_labels:
            label.new(x=i, y=float(low[i]), text="LONG\nST Flip",
                      style=label.style_label_up, color="#00e676",
                      textcolor="#000000", size="normal")
        if show_levels:
            entry_price = float(close[i])
            sl_price = float(close[i] - atr[i] * atr_mult)
            tp_price = float(close[i] + atr[i] * atr_mult * 2)
            end_bar = min(i + 30, n - 1)
            line.new(x1=i, y1=entry_price, x2=end_bar, y2=entry_price,
                     color="#42a5f5", width=1, style=line.style_dashed)
            line.new(x1=i, y1=sl_price, x2=end_bar, y2=sl_price,
                     color="#ef5350", width=1, style=line.style_dashed)
            line.new(x1=i, y1=tp_price, x2=end_bar, y2=tp_price,
                     color="#00e676", width=1, style=line.style_dashed)
            label.new(x=i + 2, y=sl_price, text="Stop Loss",
                      style=label.style_label_left, color="rgba(239,83,80,0.2)",
                      textcolor="#ef5350", size="small")
            label.new(x=i + 2, y=tp_price, text="Take Profit",
                      style=label.style_label_left, color="rgba(0,230,118,0.2)",
                      textcolor="#00e676", size="small")
            box.new(left=i, top=tp_price, right=end_bar, bottom=sl_price,
                    border_color="rgba(66,165,245,0.15)", bgcolor="rgba(66,165,245,0.03)")

    elif short_cond[i] and (i - last_signal_idx) > 20:
        last_signal_idx = i
        if show_labels:
            label.new(x=i, y=float(high[i]), text="SHORT\nST Flip",
                      style=label.style_label_down, color="#ef5350",
                      textcolor="#ffffff", size="normal")
        if show_levels:
            entry_price = float(close[i])
            sl_price = float(close[i] + atr[i] * atr_mult)
            tp_price = float(close[i] - atr[i] * atr_mult * 2)
            end_bar = min(i + 30, n - 1)
            line.new(x1=i, y1=entry_price, x2=end_bar, y2=entry_price,
                     color="#42a5f5", width=1, style=line.style_dashed)
            line.new(x1=i, y1=sl_price, x2=end_bar, y2=sl_price,
                     color="#ef5350", width=1, style=line.style_dashed)
            line.new(x1=i, y1=tp_price, x2=end_bar, y2=tp_price,
                     color="#00e676", width=1, style=line.style_dashed)
            label.new(x=i + 2, y=sl_price, text="Stop Loss",
                      style=label.style_label_left, color="rgba(239,83,80,0.2)",
                      textcolor="#ef5350", size="small")
            label.new(x=i + 2, y=tp_price, text="Take Profit",
                      style=label.style_label_left, color="rgba(0,230,118,0.2)",
                      textcolor="#00e676", size="small")
            box.new(left=i, top=sl_price, right=end_bar, bottom=tp_price,
                    border_color="rgba(239,83,80,0.15)", bgcolor="rgba(239,83,80,0.03)")

# Plots
plot(supertrend, title="Supertrend", color="blue")
plot(atr, title="ATR", color="orange")
bgcolor(vol_confirmed, color="rgba(0, 200, 0, 0.05)")
bgcolor(st_bullish, color="rgba(0, 255, 0, 0.05)")
bgcolor(st_bearish, color="rgba(255, 0, 0, 0.05)")
