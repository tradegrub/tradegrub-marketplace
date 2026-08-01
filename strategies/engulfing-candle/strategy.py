# Engulfing Candle Strategy
from tg_scripting import *

indicator("Engulfing Candle", overlay=True)

atr_len = input.int(14, "ATR Length", minval=5, maxval=50)
atr_mult = input.float(1.5, "ATR Stop Multiplier", minval=0.5, maxval=5.0)
min_body_ratio = input.float(0.6, "Min Body Ratio", minval=0.3, maxval=0.9)
show_labels = input.bool(True, "Show Labels")
show_levels = input.bool(True, "Show Entry/Stop/TP Levels")

atr = ta.atr(high, low, close, atr_len)

body = np.abs(close - open)
candle_range = high - low
body_ratio = np.where(candle_range > 0, body / candle_range, 0)

# Array-based conditions for engulfing patterns
prev_bearish = np.roll(close, 1) < np.roll(open, 1)
prev_bullish = np.roll(close, 1) > np.roll(open, 1)
curr_bullish = close > open
curr_bearish = close < open
prev_open = np.roll(open, 1)
prev_close = np.roll(close, 1)






# Bullish engulfing: prev bearish, curr bullish, curr body engulfs prev body
bullish_engulf = (prev_bearish & curr_bullish &
                  (close > prev_open) & (open < prev_close) &
                  (body_ratio >= min_body_ratio))

# Bearish engulfing: prev bullish, curr bearish, curr body engulfs prev body
bearish_engulf = (prev_bullish & curr_bearish &
                  (close < prev_open) & (open > prev_close) &
                  (body_ratio >= min_body_ratio))

n = len(close)
for i in range(1, n):
    strategy.set_bar_index(i)
    if bullish_engulf[i]:
        strategy.entry("Long", strategy.LONG)
        strategy.exit("Long SL", "Long", stop=close[i] - atr[i] * atr_mult)

    if bearish_engulf[i]:
        strategy.entry("Short", strategy.SHORT)
        strategy.exit("Short SL", "Short", stop=close[i] + atr[i] * atr_mult)

plot(body_ratio, title="Body Ratio", color="blue")
hline(min_body_ratio, title="Min Ratio", color="gray")
plotshape(bullish_engulf, title="Bull Engulf", style="triangleup", location="belowbar", color="green")
plotshape(bearish_engulf, title="Bear Engulf", style="triangledown", location="abovebar", color="red")

# Highlight the engulfing bar itself to match the glowing candle in the concept art
bgcolor([("rgba(76,175,80,0.12)" if bullish_engulf[i] else ("rgba(244,67,54,0.12)" if bearish_engulf[i] else None)) for i in range(n)])

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
