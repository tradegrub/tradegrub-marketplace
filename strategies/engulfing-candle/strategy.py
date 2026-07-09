# Engulfing Candle Strategy
from tg_scripting import *

strategy("Engulfing Candle", overlay=True)

atr_len = input.int(14, "ATR Length", minval=5, maxval=50)
atr_mult = input.float(1.5, "ATR Stop Multiplier", minval=0.5, maxval=5.0)
min_body_ratio = input.float(0.6, "Min Body Ratio", minval=0.3, maxval=0.9)
show_labels = input.bool(True, "Show Labels")
show_levels = input.bool(True, "Show Entry/Stop/TP Levels")

atr = ta.atr(high, low, close, atr_len)

body = np.abs(close - open)
candle_range = high - low
body_ratio = np.where(candle_range > 0, body / candle_range, 0)

prev_body = np.abs(close[-2] - open[-2])
curr_body = np.abs(close[-1] - open[-1])

prev_bearish = close[-2] < open[-2]
prev_bullish = close[-2] > open[-2]
curr_bullish = close[-1] > open[-1]
curr_bearish = close[-1] < open[-1]

# Bullish engulfing: prev bearish, curr bullish, curr body engulfs prev body
bullish_engulf = (prev_bearish and curr_bullish and
                  close[-1] > open[-2] and open[-1] < close[-2] and
                  body_ratio[-1] >= min_body_ratio)

# Bearish engulfing: prev bullish, curr bearish, curr body engulfs prev body
bearish_engulf = (prev_bullish and curr_bearish and
                  close[-1] < open[-2] and open[-1] > close[-2] and
                  body_ratio[-1] >= min_body_ratio)

if bullish_engulf:
    strategy.entry("Long", strategy.LONG)
    strategy.exit("Long SL", "Long", stop=close[-1] - atr[-1] * atr_mult)

if bearish_engulf:
    strategy.entry("Short", strategy.SHORT)
    strategy.exit("Short SL", "Short", stop=close[-1] + atr[-1] * atr_mult)

plot(body_ratio, title="Body Ratio", color="blue")
hline(min_body_ratio, title="Min Ratio", color="gray")
plotshape(bullish_engulf, title="Bull Engulf", style="triangleup", location="belowbar", color="green")
plotshape(bearish_engulf, title="Bear Engulf", style="triangledown", location="abovebar", color="red")

# --- Rich annotations ---
n = len(close)
prev_bearish_arr = np.roll(close, 1) < np.roll(open, 1)
prev_bullish_arr = np.roll(close, 1) > np.roll(open, 1)
curr_bullish_arr = close > open
curr_bearish_arr = close < open
prev_open_arr = np.roll(open, 1)
prev_close_arr = np.roll(close, 1)

bull_engulf_arr = (prev_bearish_arr & curr_bullish_arr &
                   (close > prev_open_arr) & (open < prev_close_arr) &
                   (body_ratio >= min_body_ratio))
bear_engulf_arr = (prev_bullish_arr & curr_bearish_arr &
                   (close < prev_open_arr) & (open > prev_close_arr) &
                   (body_ratio >= min_body_ratio))

last_signal_idx = -100
for i in range(1, n):
    if i - last_signal_idx < 15:
        continue

    if bull_engulf_arr[i]:
        last_signal_idx = i
        if show_labels:
            label.new(x=i, y=float(low[i]),
                      text="Bullish\nEngulfing",
                      style=label.style_label_up,
                      color="#00e676", textcolor="#000000", size="normal")
        if show_levels:
            entry_price = float(close[i])
            sl_price = float(close[i] - atr[i] * atr_mult)
            tp_price = float(close[i] + atr[i] * atr_mult * 2)
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

    elif bear_engulf_arr[i]:
        last_signal_idx = i
        if show_labels:
            label.new(x=i, y=float(high[i]),
                      text="Bearish\nEngulfing",
                      style=label.style_label_down,
                      color="#ef5350", textcolor="#ffffff", size="normal")
        if show_levels:
            entry_price = float(close[i])
            sl_price = float(close[i] + atr[i] * atr_mult)
            tp_price = float(close[i] - atr[i] * atr_mult * 2)
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
