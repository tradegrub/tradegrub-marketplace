# Doji Reversal Strategy
from tg_scripting import *
import numpy as np

indicator("Doji Reversal", overlay=True)

atr_len = input.int(14, "ATR Length", minval=5, maxval=50)
atr_mult = input.float(2.0, "ATR Target Multiplier", minval=1.0, maxval=5.0)
doji_pct = input.float(0.05, "Doji Body % of Range", minval=0.01, maxval=0.15)
sr_len = input.int(20, "Support/Resistance Lookback", minval=10, maxval=50)
show_labels = input.bool(True, "Show Labels")
show_levels = input.bool(True, "Show Entry/Stop/TP Levels")

atr = ta.atr(high, low, close, atr_len)
support = ta.lowest(low, sr_len)
resistance = ta.highest(high, sr_len)

body = np.abs(close - open)
candle_range = high - low
body_pct = np.where(candle_range > 0, body / candle_range, 1.0)

n = len(close)
bull_confirm = np.zeros(n, dtype=bool)
bear_confirm = np.zeros(n, dtype=bool)

for i in range(2, n):
    strategy.set_bar_index(i)
    is_doji_i = body_pct[i-1] <= doji_pct
    near_support_i = (low[i-1] - support[i-1]) < atr[i-1] * 0.3
    near_resistance_i = (resistance[i-1] - high[i-1]) < atr[i-1] * 0.3
    if is_doji_i and near_support_i and close[i] > open[i]:
        bull_confirm[i] = True
        strategy.entry("Long", strategy.LONG)
        strategy.exit("Long Exit", "Long", stop=low[i-1] - atr[i] * 0.5,
                      limit=close[i] + atr[i] * atr_mult)
    elif is_doji_i and near_resistance_i and close[i] < open[i]:
        bear_confirm[i] = True
        strategy.entry("Short", strategy.SHORT)
        strategy.exit("Short Exit", "Short", stop=high[i-1] + atr[i] * 0.5,
                      limit=close[i] - atr[i] * atr_mult)

plot(support, title="Support", color="#42a5f5")
plot(resistance, title="Resistance", color="#ef5350")
plot(body_pct, title="Body Pct", color="blue")
hline(doji_pct, title="Doji Threshold", color="gray")

doji_arr = body_pct <= doji_pct
near_support_arr = (low - support) < atr * 0.3
near_resistance_arr = (resistance - high) < atr * 0.3
doji_at_extreme = doji_arr & (near_support_arr | near_resistance_arr)

plotshape(doji_at_extreme, title="Doji", style="xcross", location="abovebar", color="#ff9800", size="small")
plotshape(bull_confirm, title="Bull Doji", style="triangleup", location="belowbar", color="#00e676")
plotshape(bear_confirm, title="Bear Doji", style="triangledown", location="abovebar", color="#ef5350")

bgcolor([("rgba(255,152,0,0.10)" if doji_at_extreme[i] else None) for i in range(n)])

# --- Rich annotations ---
last_signal_idx = -100
cooldown = 15
exit_bars = 30

for i in range(2, n):
    is_doji_i = body_pct[i - 1] <= doji_pct
    near_support_i = (low[i - 1] - support[i - 1]) < atr[i - 1] * 0.3
    near_resistance_i = (resistance[i - 1] - high[i - 1]) < atr[i - 1] * 0.3
    bull_i = is_doji_i and near_support_i and close[i] > open[i]
    bear_i = is_doji_i and near_resistance_i and close[i] < open[i]

    if bull_i and (i - last_signal_idx) > cooldown:
        last_signal_idx = i
        if show_labels:
            label.new(x=i - 1, y=float(low[i - 1]), text="Doji",
                      style=label.style_label_up, color="rgba(136,136,136,0.4)",
                      textcolor="#888888", size="small")
            label.new(x=i, y=float(low[i]), text="LONG\nBull Reversal",
                      style=label.style_label_up, color="#00e676",
                      textcolor="#000000", size="normal")
        if show_levels:
            entry_price = float(close[i])
            sl_price = float(low[i - 1] - atr[i] * 0.5)
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

    elif bear_i and (i - last_signal_idx) > cooldown:
        last_signal_idx = i
        if show_labels:
            label.new(x=i - 1, y=float(high[i - 1]), text="Doji",
                      style=label.style_label_down, color="rgba(136,136,136,0.4)",
                      textcolor="#888888", size="small")
            label.new(x=i, y=float(high[i]), text="SHORT\nBear Reversal",
                      style=label.style_label_down, color="#ef5350",
                      textcolor="#ffffff", size="normal")
        if show_levels:
            entry_price = float(close[i])
            sl_price = float(high[i - 1] + atr[i] * 0.5)
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
                    border_color="rgba(239,83,80,0.15)", bgcolor="rgba(239,83,80,0.03)")
