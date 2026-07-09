from tg_scripting import *

strategy("Wedge Breakout", overlay=True)

lookback = input.int(20, "Lookback Period", minval=10, maxval=50)
vol_mult = input.float(1.5, "Volume Multiplier", minval=1.0, maxval=3.0)
atr_mult = input.float(2.0, "ATR Stop Multiplier", minval=1.0, maxval=4.0)
min_touches = input.int(3, "Min Trendline Touches", minval=2, maxval=5)
converge_pct = input.float(0.5, "Convergence Threshold %", minval=0.1, maxval=2.0)
use_volume = input.bool(True, "Require Volume Confirmation")
tp_ratio = input.float(2.0, "Take Profit Ratio", minval=1.0, maxval=5.0)
show_wedge = input.bool(True, "Show Wedge Lines")
show_labels = input.bool(True, "Show Labels")
show_levels = input.bool(True, "Show Entry/Stop/TP Levels")

atr = ta.atr(high, low, close, 14)
vol_sma = ta.sma(volume, 20)

upper_line = ta.highest(high, lookback)
lower_line = ta.lowest(low, lookback)

upper_slope = ta.linreg(upper_line, lookback)
lower_slope = ta.linreg(lower_line, lookback)

wedge_width = upper_line - lower_line
prev_width = np.roll(wedge_width, 1)
prev_width[0] = wedge_width[0]
converging = wedge_width < prev_width * (1.0 - converge_pct / 100.0)

rising_wedge = converging & (upper_slope > 0) & (lower_slope > 0)
falling_wedge = converging & (upper_slope < 0) & (lower_slope < 0)

vol_surge = volume > vol_sma * vol_mult if use_volume else (volume > 0)
break_up = (close > upper_line) & vol_surge
break_down = (close < lower_line) & vol_surge

if show_wedge:
    plot(upper_line, title="Upper Trendline", color="red")
    plot(lower_line, title="Lower Trendline", color="green")

n = len(close)
last_signal_idx = -100
wedge_label_placed = False

for i in range(len(close)):
    if falling_wedge[i] & break_up[i]:
        strategy.entry("Long", strategy.LONG)
        plotshape(i, title="Bull Breakout", style="triangleup", color="green")

    if rising_wedge[i] & break_down[i]:
        strategy.entry("Short", strategy.SHORT)
        plotshape(i, title="Bear Breakout", style="triangledown", color="red")

    if strategy.position_size > 0:
        stop = strategy.position_avg_price - atr[i] * atr_mult
        target = strategy.position_avg_price + atr[i] * atr_mult * tp_ratio
        if close[i] <= stop or close[i] >= target:
            strategy.close("Long")

    if strategy.position_size < 0:
        stop = strategy.position_avg_price + atr[i] * atr_mult
        target = strategy.position_avg_price - atr[i] * atr_mult * tp_ratio
        if close[i] >= stop or close[i] <= target:
            strategy.close("Short")

    # --- Rich annotations ---
    if show_labels and not wedge_label_placed and (falling_wedge[i] or rising_wedge[i]):
        wedge_type = "Falling Wedge" if falling_wedge[i] else "Rising Wedge"
        label.new(x=i, y=float(upper_line[i]), text=wedge_type,
                  style=label.style_label_down, color="rgba(136,136,136,0.2)",
                  textcolor="#888888", size="normal")
        wedge_label_placed = True

    if not (falling_wedge[i] or rising_wedge[i]):
        wedge_label_placed = False

    if falling_wedge[i] and break_up[i] and (i - last_signal_idx) > 20:
        last_signal_idx = i
        if show_labels:
            label.new(x=i, y=float(low[i]), text="BREAKOUT\nLONG",
                      style=label.style_label_up, color="#00e676",
                      textcolor="#000000", size="normal")
        if show_levels:
            entry_price = float(close[i])
            sl_price = float(close[i] - atr[i] * atr_mult)
            tp_price = float(close[i] + atr[i] * atr_mult * tp_ratio)
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

    elif rising_wedge[i] and break_down[i] and (i - last_signal_idx) > 20:
        last_signal_idx = i
        if show_labels:
            label.new(x=i, y=float(high[i]), text="BREAKDOWN\nSHORT",
                      style=label.style_label_down, color="#ef5350",
                      textcolor="#ffffff", size="normal")
        if show_levels:
            entry_price = float(close[i])
            sl_price = float(close[i] + atr[i] * atr_mult)
            tp_price = float(close[i] - atr[i] * atr_mult * tp_ratio)
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
