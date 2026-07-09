# Three Bar Reversal Strategy
from tg_scripting import *
import numpy as np

indicator("Three Bar Reversal", overlay=True)

atr_len = input.int(14, "ATR Length", minval=5, maxval=50)
atr_mult = input.float(2.0, "ATR Target Multiplier", minval=1.0, maxval=5.0)
trend_len = input.int(50, "Trend EMA Length", minval=20, maxval=200)
show_labels = input.bool(True, "Show Labels")
show_levels = input.bool(True, "Show Entry/Stop/TP Levels")

atr = ta.atr(high, low, close, atr_len)
trend_ema = ta.ema(close, trend_len)

# Three bar bullish reversal: bar1 bearish, bar2 lower low + lower close, bar3 bullish closes above bar1 high
bar1_bear = np.roll(close, 2) < np.roll(open, 2)
bar2_lower = (np.roll(low, 1) < np.roll(low, 2)) & (np.roll(close, 1) < np.roll(close, 2))
bar3_bull_close = (close > open) & (close > np.roll(high, 2))
bull_3bar = bar1_bear & bar2_lower & bar3_bull_close

# Three bar bearish reversal: bar1 bullish, bar2 higher high + higher close, bar3 bearish closes below bar1 low
bar1_bull = np.roll(close, 2) > np.roll(open, 2)
bar2_higher = (np.roll(high, 1) > np.roll(high, 2)) & (np.roll(close, 1) > np.roll(close, 2))
bar3_bear_close = (close < open) & (close < np.roll(low, 2))
bear_3bar = bar1_bull & bar2_higher & bar3_bear_close

n = len(close)
for i in range(3, n):
    strategy.set_bar_index(i)
    if bull_3bar[i]:
        strategy.entry("Long", strategy.LONG)
        strategy.exit("Long Exit", "Long", stop=low[i-1] - atr[i] * 0.5,
                      limit=close[i] + atr[i] * atr_mult)

    if bear_3bar[i]:
        strategy.entry("Short", strategy.SHORT)
        strategy.exit("Short Exit", "Short", stop=high[i-1] + atr[i] * 0.5,
                  limit=close[i] - atr[i] * atr_mult)

plot(trend_ema, title="Trend EMA", color="orange")
plotshape(bull_3bar, title="Bull 3-Bar", style="triangleup", location="belowbar", color="green")
plotshape(bear_3bar, title="Bear 3-Bar", style="triangledown", location="abovebar", color="red")

bgcolor([("rgba(76,175,80,0.08)" if bull_close[i] else None) for i in range(n)], title="Bull Zone")
bgcolor([("rgba(244,67,54,0.08)" if bear[i] else None) for i in range(n)], title="Bear Zone")
# --- Rich annotations ---
n = len(close)
exit_bars = 30
last_signal_idx = -100

for i in range(3, n):
    b1_bear = close[i-2] < open[i-2]
    b2_lower = low[i-1] < low[i-2] and close[i-1] < close[i-2]
    b3_bull = close[i] > open[i] and close[i] > high[i-2]
    is_bull = b1_bear and b2_lower and b3_bull

    b1_bull = close[i-2] > open[i-2]
    b2_higher = high[i-1] > high[i-2] and close[i-1] > close[i-2]
    b3_bear = close[i] < open[i] and close[i] < low[i-2]
    is_bear = b1_bull and b2_higher and b3_bear

    if is_bull and (i - last_signal_idx) > 15:
        last_signal_idx = i
        if show_labels:
            label.new(x=i, y=float(low[i]), text="Bull 3-Bar",
                      style=label.style_label_up, color="#00e676",
                      textcolor="#000000", size="normal")
        if show_levels:
            entry_price = float(close[i])
            sl_price = float(low[i-1] - atr[i] * 0.5)
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
            label.new(x=i, y=float(high[i]), text="Bear 3-Bar",
                      style=label.style_label_down, color="#ef5350",
                      textcolor="#ffffff", size="normal")
        if show_levels:
            entry_price = float(close[i])
            sl_price = float(high[i-1] + atr[i] * 0.5)
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
            box.new(left=i, top=max(tp_price, sl_price), right=end_bar, bottom=min(tp_price, sl_price),
                    border_color="rgba(239,83,80,0.15)", bgcolor="rgba(239,83,80,0.03)")
