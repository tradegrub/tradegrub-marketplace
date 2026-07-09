from tg_scripting import *
import numpy as np

indicator("Triangle Breakout", overlay=True)

lookback = input.int(50, "Lookback Period", minval=20, maxval=100)
pivot_len = input.int(5, "Pivot Length", minval=2, maxval=10)
rsi_len = input.int(14, "RSI Length", minval=5, maxval=30)
rsi_bull = input.float(50.0, "RSI Bull Threshold", minval=40.0, maxval=60.0)
rsi_bear = input.float(50.0, "RSI Bear Threshold", minval=40.0, maxval=60.0)
atr_mult = input.float(1.5, "ATR Stop Multiplier", minval=0.5, maxval=4.0)
atr_len = input.int(14, "ATR Length", minval=5, maxval=30)
use_volume = input.bool(True, "Volume Confirmation")
show_labels = input.bool(True, "Show Labels")
show_levels = input.bool(True, "Show Entry/Stop/TP Levels")

rsi = ta.rsi(close, rsi_len)
atr = ta.atr(high, low, close, atr_len)
vol_sma = ta.sma(volume, 20)

pivot_high = ta.highest(high, pivot_len)
pivot_low = ta.lowest(low, pivot_len)

upper_slope = ta.linreg(pivot_high, lookback)
lower_slope = ta.linreg(pivot_low, lookback)

upper_line = ta.highest(high, lookback)
lower_line = ta.lowest(low, lookback)
mid_line = (upper_line + lower_line) / 2

range_width = upper_line - lower_line
prev_upper = np.roll(upper_line, pivot_len)
prev_upper[:pivot_len] = np.nan
prev_lower = np.roll(lower_line, pivot_len)
prev_lower[:pivot_len] = np.nan
prev_width = prev_upper - prev_lower
converging = range_width < prev_width

hh_now = ta.highest(high, lookback)
hh_prev = np.roll(hh_now, lookback // 2)
hh_prev[:lookback // 2] = np.nan
flat_top = np.abs(hh_now - hh_prev) < atr * 0.5
ll_now = ta.lowest(low, lookback)
ll_prev = np.roll(ll_now, lookback // 2)
ll_prev[:lookback // 2] = np.nan
flat_bot = np.abs(ll_now - ll_prev) < atr * 0.5

ascending = converging & flat_top & ~flat_bot
descending = converging & ~flat_top & flat_bot
symmetrical = converging & ~flat_top & ~flat_bot

prev_upper_1 = np.roll(upper_line, 1)
prev_upper_1[0] = np.nan
prev_lower_1 = np.roll(lower_line, 1)
prev_lower_1[0] = np.nan
bull_break = (close > prev_upper_1) & (rsi > rsi_bull)
bear_break = (close < prev_lower_1) & (rsi < rsi_bear)

if use_volume:
    bull_break = bull_break & (volume > vol_sma * 1.2)
    bear_break = bear_break & (volume > vol_sma * 1.2)

upper_plot = plot(upper_line, title="Upper", color="red")
lower_plot = plot(lower_line, title="Lower", color="green")
plot(mid_line, title="Mid", color="gray", linewidth=1)
fill(upper_plot, lower_plot, color="rgba(66,165,245,0.06)", title="Triangle Zone")

bgcolor(ascending, color="rgba(0,200,0,0.05)")
bgcolor(descending, color="rgba(200,0,0,0.05)")
bgcolor(symmetrical, color="rgba(0,0,200,0.05)")

plotshape(bull_break & (ascending | symmetrical), style="triangleup", location="belowbar", color="green", size="small")
plotshape(bear_break & (descending | symmetrical), style="triangledown", location="abovebar", color="red", size="small")

n = len(close)
last_signal_idx = -100
triangle_label_placed = False

for i in range(len(close)):
    strategy.set_bar_index(i)
    if bull_break[i] and (ascending[i] or symmetrical[i]):
        strategy.entry("Long", strategy.LONG)
    elif bear_break[i] and (descending[i] or symmetrical[i]):
        strategy.entry("Short", strategy.SHORT)

    if strategy.position_size > 0 and close[i] < close[i] - atr[i] * atr_mult:
        strategy.close("Long")
    elif strategy.position_size < 0 and close[i] > close[i] + atr[i] * atr_mult:
        strategy.close("Short")

    # --- Rich annotations ---
    if show_labels and not triangle_label_placed and converging[i]:
        tri_type = "Ascending" if ascending[i] else ("Descending" if descending[i] else ("Symmetrical" if symmetrical[i] else ""))
        if tri_type:
            label.new(x=i, y=float(upper_line[i]), text=tri_type + " Triangle",
                      style=label.style_label_down, color="rgba(136,136,136,0.2)",
                      textcolor="#888888", size="normal")
            triangle_label_placed = True

    if bull_break[i] and (ascending[i] or symmetrical[i]) and (i - last_signal_idx) > 20:
        last_signal_idx = i
        if show_labels:
            label.new(x=i, y=float(low[i]), text="BREAKOUT",
                      style=label.style_label_up, color="#00e676",
                      textcolor="#000000", size="normal")
        if show_levels:
            entry_price = float(close[i])
            sl_price = float(lower_line[i])
            tp_price = entry_price + (entry_price - sl_price) * 2
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

    elif bear_break[i] and (descending[i] or symmetrical[i]) and (i - last_signal_idx) > 20:
        last_signal_idx = i
        if show_labels:
            label.new(x=i, y=float(high[i]), text="BREAKDOWN",
                      style=label.style_label_down, color="#ef5350",
                      textcolor="#ffffff", size="normal")
        if show_levels:
            entry_price = float(close[i])
            sl_price = float(upper_line[i])
            tp_price = entry_price - (sl_price - entry_price) * 2
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
