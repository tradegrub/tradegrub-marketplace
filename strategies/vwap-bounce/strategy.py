# VWAP Bounce/Rejection Strategy
from tg_scripting import *
import numpy as np

indicator("VWAP Bounce", overlay=True)

atr_len = input.int(14, "ATR Length", minval=5, maxval=50)
bounce_mult = input.float(0.5, "Bounce ATR Multiplier", minval=0.1, maxval=2.0)
exit_mult = input.float(1.5, "Exit ATR Multiplier", minval=0.5, maxval=5.0)
trend_len = input.int(50, "Trend SMA Length", minval=10, maxval=200)
show_labels = input.bool(True, "Show Labels")
show_levels = input.bool(True, "Show Entry/Stop/TP Levels")

vwap_val = ta.vwap(high, low, close, volume)
atr = ta.atr(high, low, close, atr_len)
trend_sma = ta.sma(close, trend_len)

# Price near VWAP (within bounce_mult * ATR)
near_vwap = np.abs(close - vwap_val) < bounce_mult * atr

# Bullish bounce: price near VWAP in uptrend
bull_bounce = near_vwap & (close > trend_sma) & (close > vwap_val)
# Bearish rejection: price near VWAP in downtrend
bear_reject = near_vwap & (close < trend_sma) & (close < vwap_val)

if bull_bounce[-1]:
    strategy.entry("Long", strategy.LONG)
if bear_reject[-1]:
    strategy.entry("Short", strategy.SHORT)

# Exit when price moves away from VWAP by exit_mult * ATR
long_exit = close[-1] > vwap_val[-1] + exit_mult * atr[-1]
short_exit = close[-1] < vwap_val[-1] - exit_mult * atr[-1]

if long_exit:
    strategy.close("Long")
if short_exit:
    strategy.close("Short")

plot(vwap_val, title="VWAP", color="blue")
plot(trend_sma, title="Trend SMA", color="orange")
bgcolor(bull_bounce[-1], color="rgba(0,255,0,0.1)")
bgcolor(bear_reject[-1], color="rgba(255,0,0,0.1)")

# --- Rich annotations ---
n = len(close)
last_signal_idx = -100

for i in range(trend_len, n):
    if bull_bounce[i] and (i - last_signal_idx) > 20:
        last_signal_idx = i
        if show_labels:
            label.new(x=i, y=float(low[i]), text="VWAP Bounce\nLONG",
                      style=label.style_label_up, color="#00e676",
                      textcolor="#000000", size="normal")
        if show_levels:
            entry_price = float(close[i])
            sl_price = float(vwap_val[i] - atr[i])
            tp_price = float(vwap_val[i] + exit_mult * atr[i])
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

    elif bear_reject[i] and (i - last_signal_idx) > 20:
        last_signal_idx = i
        if show_labels:
            label.new(x=i, y=float(high[i]), text="VWAP Reject\nSHORT",
                      style=label.style_label_down, color="#ef5350",
                      textcolor="#ffffff", size="normal")
        if show_levels:
            entry_price = float(close[i])
            sl_price = float(vwap_val[i] + atr[i])
            tp_price = float(vwap_val[i] - exit_mult * atr[i])
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
