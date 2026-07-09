# Hammer Reversal Strategy
from tg_scripting import *

indicator("Hammer Reversal", overlay=True)

atr_len = input.int(14, "ATR Length", minval=5, maxval=50)
atr_mult = input.float(1.5, "ATR Stop Multiplier", minval=0.5, maxval=5.0)
wick_ratio = input.float(2.0, "Min Wick-to-Body Ratio", minval=1.5, maxval=5.0)
trend_len = input.int(20, "Trend SMA Length", minval=10, maxval=50)
show_labels = input.bool(True, "Show Labels")
show_levels = input.bool(True, "Show Entry/Stop/TP Levels")

atr = ta.atr(high, low, close, atr_len)
trend_sma = ta.sma(close, trend_len)

body = np.abs(close - open)
upper_wick = high - np.maximum(close, open)
lower_wick = np.minimum(close, open) - low
candle_range = high - low

# Hammer: small body at top, long lower wick, in downtrend
is_hammer = ((lower_wick[-1] > body[-1] * wick_ratio) and
             (upper_wick[-1] < body[-1] * 0.5) and
             (body[-1] > 0) and
             (close[-1] < trend_sma[-1]))

# Shooting star: small body at bottom, long upper wick, in uptrend
is_shooting_star = ((upper_wick[-1] > body[-1] * wick_ratio) and
                    (lower_wick[-1] < body[-1] * 0.5) and
                    (body[-1] > 0) and
                    (close[-1] > trend_sma[-1]))

if is_hammer:
    strategy.entry("Long", strategy.LONG)
    strategy.exit("Long SL", "Long", stop=low[-1] - atr[-1] * 0.5,
                  limit=close[-1] + atr[-1] * atr_mult)

if is_shooting_star:
    strategy.entry("Short", strategy.SHORT)
    strategy.exit("Short SL", "Short", stop=high[-1] + atr[-1] * 0.5,
                  limit=close[-1] - atr[-1] * atr_mult)

plot(trend_sma, title="Trend SMA", color="orange")
plotshape(is_hammer, title="Hammer", style="triangleup", location="belowbar", color="green")
plotshape(is_shooting_star, title="Shooting Star", style="triangledown", location="abovebar", color="red")

# --- Rich annotations ---
n = len(close)
hammer_arr = ((lower_wick > body * wick_ratio) &
              (upper_wick < body * 0.5) &
              (body > 0) &
              (close < trend_sma))
star_arr = ((upper_wick > body * wick_ratio) &
            (lower_wick < body * 0.5) &
            (body > 0) &
            (close > trend_sma))
last_signal_idx = -100

for i in range(1, n):
    if i - last_signal_idx < 15:
        continue

    if hammer_arr[i]:
        last_signal_idx = i
        if show_labels:
            label.new(x=i, y=float(low[i]),
                      text="Hammer",
                      style=label.style_label_up,
                      color="#00e676", textcolor="#000000", size="normal")
        if show_levels:
            entry_price = float(close[i])
            sl_price = float(low[i] - atr[i] * 0.5)
            tp_price = float(close[i] + atr[i] * atr_mult)
            end_bar = min(i + 20, n - 1)
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

    elif star_arr[i]:
        last_signal_idx = i
        if show_labels:
            label.new(x=i, y=float(high[i]),
                      text="Shooting Star",
                      style=label.style_label_down,
                      color="#ef5350", textcolor="#ffffff", size="normal")
        if show_levels:
            entry_price = float(close[i])
            sl_price = float(high[i] + atr[i] * 0.5)
            tp_price = float(close[i] - atr[i] * atr_mult)
            end_bar = min(i + 20, n - 1)
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
                    border_color="rgba(239,83,80,0.15)", bgcolor="rgba(239,83,80,0.03)")
