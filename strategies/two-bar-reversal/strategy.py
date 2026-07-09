# Two Bar Reversal Strategy
from tg_scripting import *
import numpy as np

strategy("Two Bar Reversal", overlay=True)

atr_len = input.int(14, "ATR Length", minval=5, maxval=50)
atr_mult = input.float(1.5, "ATR Target Multiplier", minval=1.0, maxval=5.0)
min_body = input.float(0.5, "Min Body Ratio", minval=0.3, maxval=0.8)
show_labels = input.bool(True, "Show Labels")
show_levels = input.bool(True, "Show Entry/Stop/TP Levels")

atr = ta.atr(high, low, close, atr_len)

body = np.abs(close - open)
candle_range = high - low
body_ratio = np.where(candle_range > 0, body / candle_range, 0)

# Bullish two-bar reversal: strong bearish bar followed by strong bullish bar
# Bar 2 close > Bar 1 open, Bar 2 open < Bar 1 close
bar1_bearish = close[-2] < open[-2] and body_ratio[-2] >= min_body
bar2_bullish = close[-1] > open[-1] and body_ratio[-1] >= min_body

bull_2bar = (bar1_bearish and bar2_bullish and
             close[-1] > open[-2] and open[-1] <= close[-2])

# Bearish two-bar reversal: strong bullish bar followed by strong bearish bar
bar1_bullish = close[-2] > open[-2] and body_ratio[-2] >= min_body
bar2_bearish = close[-1] < open[-1] and body_ratio[-1] >= min_body

bear_2bar = (bar1_bullish and bar2_bearish and
             close[-1] < open[-2] and open[-1] >= close[-2])

if bull_2bar:
    strategy.entry("Long", strategy.LONG)
    strategy.exit("Long Exit", "Long",
                  stop=min(low[-1], low[-2]) - atr[-1] * 0.3,
                  limit=close[-1] + atr[-1] * atr_mult)

if bear_2bar:
    strategy.entry("Short", strategy.SHORT)
    strategy.exit("Short Exit", "Short",
                  stop=max(high[-1], high[-2]) + atr[-1] * 0.3,
                  limit=close[-1] - atr[-1] * atr_mult)

plot(body_ratio, title="Body Ratio", color="blue")
hline(min_body, title="Min Body", color="gray")
plotshape(bull_2bar, title="Bull 2-Bar", style="triangleup", location="belowbar", color="green")
plotshape(bear_2bar, title="Bear 2-Bar", style="triangledown", location="abovebar", color="red")

# --- Rich annotations ---
n = len(close)
exit_bars = 30
last_signal_idx = -100

for i in range(2, n):
    b1_bear_i = close[i-1] < open[i-1] and body_ratio[i-1] >= min_body
    b2_bull_i = close[i] > open[i] and body_ratio[i] >= min_body
    is_bull = b1_bear_i and b2_bull_i and close[i] > open[i-1] and open[i] <= close[i-1]

    b1_bull_i = close[i-1] > open[i-1] and body_ratio[i-1] >= min_body
    b2_bear_i = close[i] < open[i] and body_ratio[i] >= min_body
    is_bear = b1_bull_i and b2_bear_i and close[i] < open[i-1] and open[i] >= close[i-1]

    if is_bull and (i - last_signal_idx) > 15:
        last_signal_idx = i
        if show_labels:
            label.new(x=i, y=float(low[i]), text="Bull 2-Bar",
                      style=label.style_label_up, color="#00e676",
                      textcolor="#000000", size="normal")
        if show_levels:
            entry_price = float(close[i])
            sl_price = float(min(low[i], low[i-1]) - atr[i] * 0.3)
            tp_price = float(close[i] + atr[i] * atr_mult)
            end_bar = min(i + exit_bars, n - 1)
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

    elif is_bear and (i - last_signal_idx) > 15:
        last_signal_idx = i
        if show_labels:
            label.new(x=i, y=float(high[i]), text="Bear 2-Bar",
                      style=label.style_label_down, color="#ef5350",
                      textcolor="#ffffff", size="normal")
        if show_levels:
            entry_price = float(close[i])
            sl_price = float(max(high[i], high[i-1]) + atr[i] * 0.3)
            tp_price = float(close[i] - atr[i] * atr_mult)
            end_bar = min(i + exit_bars, n - 1)
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
