# Pin Bar Reversal Strategy
from tg_scripting import *
import numpy as np

strategy("Pin Bar", overlay=True)

atr_len = input.int(14, "ATR Length", minval=5, maxval=50)
atr_mult = input.float(2.0, "ATR Target Multiplier", minval=1.0, maxval=5.0)
nose_ratio = input.float(0.33, "Max Nose Ratio", minval=0.1, maxval=0.5)
tail_ratio = input.float(0.6, "Min Tail Ratio", minval=0.4, maxval=0.8)
trend_len = input.int(20, "Trend SMA Length", minval=10, maxval=50)
show_labels = input.bool(True, "Show Labels")
show_levels = input.bool(True, "Show Entry/Stop/TP Levels")

atr = ta.atr(high, low, close, atr_len)
trend_sma = ta.sma(close, trend_len)

body = np.abs(close - open)
candle_range = high - low
upper_wick = high - np.maximum(close, open)
lower_wick = np.minimum(close, open) - low

body_ratio = np.where(candle_range > 0, body / candle_range, 1.0)
upper_ratio = np.where(candle_range > 0, upper_wick / candle_range, 0)
lower_ratio = np.where(candle_range > 0, lower_wick / candle_range, 0)

# Bullish pin bar: long lower tail, small body near top
bull_pin = (body_ratio[-1] <= nose_ratio and
            lower_ratio[-1] >= tail_ratio and
            close[-1] < trend_sma[-1])

# Bearish pin bar: long upper tail, small body near bottom
bear_pin = (body_ratio[-1] <= nose_ratio and
            upper_ratio[-1] >= tail_ratio and
            close[-1] > trend_sma[-1])

if bull_pin:
    strategy.entry("Long", strategy.LONG)
    strategy.exit("Long Exit", "Long", stop=low[-1] - atr[-1] * 0.3,
                  limit=close[-1] + atr[-1] * atr_mult)

if bear_pin:
    strategy.entry("Short", strategy.SHORT)
    strategy.exit("Short Exit", "Short", stop=high[-1] + atr[-1] * 0.3,
                  limit=close[-1] - atr[-1] * atr_mult)

plot(trend_sma, title="Trend SMA", color="orange")
plot(body_ratio, title="Body Ratio", color="blue")
plotshape(bull_pin, title="Bull Pin", style="triangleup", location="belowbar", color="green")
plotshape(bear_pin, title="Bear Pin", style="triangledown", location="abovebar", color="red")

# --- Rich annotations ---
n = len(close)
last_signal_idx = -100
exit_bars = 20
cooldown = 15

bull_pin_arr = (body_ratio <= nose_ratio) & (lower_ratio >= tail_ratio) & (close < trend_sma)
bear_pin_arr = (body_ratio <= nose_ratio) & (upper_ratio >= tail_ratio) & (close > trend_sma)

for i in range(trend_len, n):
    if bull_pin_arr[i] and (i - last_signal_idx) > cooldown:
        last_signal_idx = i
        if show_labels:
            label.new(x=i, y=float(low[i]), text="Pin Bar\nLONG",
                      style=label.style_label_up, color="#00e676",
                      textcolor="#000000", size="normal")
        if show_levels:
            entry_price = float(close[i])
            sl_price = float(low[i] - atr[i] * 0.3)
            tp_price = float(close[i] + atr[i] * atr_mult)
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

    elif bear_pin_arr[i] and (i - last_signal_idx) > cooldown:
        last_signal_idx = i
        if show_labels:
            label.new(x=i, y=float(high[i]), text="Pin Bar\nSHORT",
                      style=label.style_label_down, color="#ef5350",
                      textcolor="#ffffff", size="normal")
        if show_levels:
            entry_price = float(close[i])
            sl_price = float(high[i] + atr[i] * 0.3)
            tp_price = float(close[i] - atr[i] * atr_mult)
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
