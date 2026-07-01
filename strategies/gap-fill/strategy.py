# Gap Fill Reversion Strategy
from tg_scripting import *
import numpy as np

indicator("Gap Fill", overlay=True)

min_gap_atr = input.float(0.5, "Min Gap Size (ATR mult)", minval=0.2, maxval=3.0)
atr_len = input.int(14, "ATR Length", minval=5, maxval=50)
atr_stop = input.float(1.5, "ATR Stop Multiplier", minval=0.5, maxval=5.0)
max_bars = input.int(10, "Max Bars to Fill", minval=3, maxval=30)
show_labels = input.bool(True, "Show Labels")
show_levels = input.bool(True, "Show Entry/Stop/TP Levels")

atr = ta.atr(high, low, close, atr_len)

# Detect gap: current open vs previous close (element-wise)
prev_close = np.roll(close, 1)
prev_close[0] = close[0]
gap_up = open - prev_close
gap_down = prev_close - open
prev_atr = np.roll(atr, 1)
prev_atr[0] = atr[0]
is_gap_up = gap_up > prev_atr * min_gap_atr
is_gap_down = gap_down > prev_atr * min_gap_atr

# Fade the gap: expect price to fill back toward prior close
n = len(close)
last_signal_idx = -100

for i in range(1, len(close)):
    if is_gap_up[i]:
        strategy.entry("Short Gap", strategy.SHORT)
        strategy.exit("Short Exit", "Short Gap",
                      limit=prev_close[i],
                      stop=open[i] + atr[i] * atr_stop)

        if i - last_signal_idx >= 15:
            last_signal_idx = i
            if show_labels:
                label.new(x=i, y=float(high[i]),
                          text="Gap Up\nFade SHORT",
                          style=label.style_label_down,
                          color="#ef5350", textcolor="#ffffff", size="normal")
            if show_levels:
                entry_price = float(open[i])
                sl_price = float(open[i] + atr[i] * atr_stop)
                tp_price = float(prev_close[i])
                end_bar = min(i + max_bars, n - 1)
                line.new(x1=i, y1=entry_price, x2=end_bar, y2=entry_price,
                         color="#42a5f5", width=1, style=line.style_dashed)
                line.new(x1=i, y1=sl_price, x2=end_bar, y2=sl_price,
                         color="#ef5350", width=1, style=line.style_dashed)
                label.new(x=i + 2, y=sl_price, text="Stop Loss",
                          style=label.style_label_left, color="rgba(239,83,80,0.2)",
                          textcolor="#ef5350", size="small")
                line.new(x1=i, y1=tp_price, x2=end_bar, y2=tp_price,
                         color="#00e676", width=1, style=line.style_dashed)
                label.new(x=i + 2, y=tp_price, text="Gap Fill Target",
                          style=label.style_label_left, color="rgba(0,230,118,0.2)",
                          textcolor="#00e676", size="small")
                box.new(left=i, top=sl_price, right=end_bar, bottom=tp_price,
                        border_color="rgba(239,83,80,0.15)", bgcolor="rgba(239,83,80,0.03)")

    if is_gap_down[i]:
        strategy.entry("Long Gap", strategy.LONG)
        strategy.exit("Long Exit", "Long Gap",
                      limit=prev_close[i],
                      stop=open[i] - atr[i] * atr_stop)

        if i - last_signal_idx >= 15:
            last_signal_idx = i
            if show_labels:
                label.new(x=i, y=float(low[i]),
                          text="Gap Down\nFade LONG",
                          style=label.style_label_up,
                          color="#00e676", textcolor="#000000", size="normal")
            if show_levels:
                entry_price = float(open[i])
                sl_price = float(open[i] - atr[i] * atr_stop)
                tp_price = float(prev_close[i])
                end_bar = min(i + max_bars, n - 1)
                line.new(x1=i, y1=entry_price, x2=end_bar, y2=entry_price,
                         color="#42a5f5", width=1, style=line.style_dashed)
                line.new(x1=i, y1=sl_price, x2=end_bar, y2=sl_price,
                         color="#ef5350", width=1, style=line.style_dashed)
                label.new(x=i + 2, y=sl_price, text="Stop Loss",
                          style=label.style_label_left, color="rgba(239,83,80,0.2)",
                          textcolor="#ef5350", size="small")
                line.new(x1=i, y1=tp_price, x2=end_bar, y2=tp_price,
                         color="#00e676", width=1, style=line.style_dashed)
                label.new(x=i + 2, y=tp_price, text="Gap Fill Target",
                          style=label.style_label_left, color="rgba(0,230,118,0.2)",
                          textcolor="#00e676", size="small")
                box.new(left=i, top=tp_price, right=end_bar, bottom=sl_price,
                        border_color="rgba(66,165,245,0.15)", bgcolor="rgba(66,165,245,0.03)")

# Plot gap levels
gap_size = open - prev_close
plot(gap_size, title="Gap Size", color="purple")
hline(0, title="Zero Line", color="gray")
plotshape(is_gap_up, title="Gap Up", style="triangledown", location="abovebar", color="red")
plotshape(is_gap_down, title="Gap Down", style="triangleup", location="belowbar", color="green")
