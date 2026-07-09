from tg_scripting import *
import numpy as np

strategy("Ichimoku RSI", overlay=True)

# Inputs
tenkan_len = input.int(9, "Tenkan-sen Period", minval=2, maxval=50)
kijun_len = input.int(26, "Kijun-sen Period", minval=5, maxval=100)
senkou_b_len = input.int(52, "Senkou Span B Period", minval=10, maxval=200)
rsi_len = input.int(14, "RSI Length", minval=2, maxval=50)
rsi_ob = input.int(70, "RSI Overbought", minval=50, maxval=90)
rsi_os = input.int(30, "RSI Oversold", minval=10, maxval=50)
show_labels = input.bool(True, "Show Labels")
show_levels = input.bool(True, "Show Entry/Stop/TP Levels")

# Calculations
tenkan, kijun, senkou_a, senkou_b, chikou = ta.ichimoku(high, low, close, tenkan_len, kijun_len, senkou_b_len)
rsi = ta.rsi(close, rsi_len)

# Cloud bullish: price above both senkou spans, tenkan above kijun
cloud_top = np.maximum(senkou_a, senkou_b)
cloud_bot = np.minimum(senkou_a, senkou_b)

long_cond = (close > cloud_top) & (tenkan > kijun) & (rsi > 50) & (rsi < rsi_ob)
short_cond = (close < cloud_bot) & (tenkan < kijun) & (rsi < 50) & (rsi > rsi_os)

atr_ann = ta.atr(high, low, close, 14)
n = len(close)
last_signal_idx = -100

for i in range(len(close)):
    if long_cond[i]:
        strategy.entry("Long", strategy.LONG)
    elif short_cond[i]:
        strategy.entry("Short", strategy.SHORT)

    if i - last_signal_idx < 20:
        continue

    if long_cond[i]:
        last_signal_idx = i
        if show_labels:
            label.new(x=i, y=float(low[i]),
                      text="Cloud + RSI\nLONG",
                      style=label.style_label_up,
                      color="#00e676", textcolor="#000000", size="normal")
        if show_levels:
            entry_price = float(close[i])
            sl_price = float(cloud_bot[i])
            tp_price = float(close[i] + (close[i] - cloud_bot[i]) * 2)
            end_bar = min(i + 30, n - 1)
            line.new(x1=i, y1=entry_price, x2=end_bar, y2=entry_price,
                     color="#42a5f5", width=1, style=line.style_dashed)
            label.new(x=i + 2, y=entry_price, text="Entry",
                      style=label.style_label_left, color="rgba(66,165,245,0.2)",
                      textcolor="#42a5f5", size="small")
            line.new(x1=i, y1=sl_price, x2=end_bar, y2=sl_price,
                     color="#ef5350", width=1, style=line.style_dashed)
            label.new(x=i + 2, y=sl_price, text="Cloud Support",
                      style=label.style_label_left, color="rgba(239,83,80,0.2)",
                      textcolor="#ef5350", size="small")
            line.new(x1=i, y1=tp_price, x2=end_bar, y2=tp_price,
                     color="#00e676", width=1, style=line.style_dashed)
            label.new(x=i + 2, y=tp_price, text="Take Profit",
                      style=label.style_label_left, color="rgba(0,230,118,0.2)",
                      textcolor="#00e676", size="small")
            box.new(left=i, top=tp_price, right=end_bar, bottom=sl_price,
                    border_color="rgba(66,165,245,0.15)", bgcolor="rgba(66,165,245,0.03)")

    elif short_cond[i]:
        last_signal_idx = i
        if show_labels:
            label.new(x=i, y=float(high[i]),
                      text="Cloud + RSI\nSHORT",
                      style=label.style_label_down,
                      color="#ef5350", textcolor="#ffffff", size="normal")
        if show_levels:
            entry_price = float(close[i])
            sl_price = float(cloud_top[i])
            tp_price = float(close[i] - (cloud_top[i] - close[i]) * 2)
            end_bar = min(i + 30, n - 1)
            line.new(x1=i, y1=entry_price, x2=end_bar, y2=entry_price,
                     color="#42a5f5", width=1, style=line.style_dashed)
            line.new(x1=i, y1=sl_price, x2=end_bar, y2=sl_price,
                     color="#ef5350", width=1, style=line.style_dashed)
            label.new(x=i + 2, y=sl_price, text="Cloud Resistance",
                      style=label.style_label_left, color="rgba(239,83,80,0.2)",
                      textcolor="#ef5350", size="small")
            line.new(x1=i, y1=tp_price, x2=end_bar, y2=tp_price,
                     color="#00e676", width=1, style=line.style_dashed)
            label.new(x=i + 2, y=tp_price, text="Take Profit",
                      style=label.style_label_left, color="rgba(0,230,118,0.2)",
                      textcolor="#00e676", size="small")
            box.new(left=i, top=sl_price, right=end_bar, bottom=tp_price,
                    border_color="rgba(239,83,80,0.15)", bgcolor="rgba(239,83,80,0.03)")

# Plots
plot(tenkan, title="Tenkan-sen", color="blue")
plot(kijun, title="Kijun-sen", color="red")
p_a = plot(senkou_a, title="Senkou A", color="green")
p_b = plot(senkou_b, title="Senkou B", color="maroon")
fill(p_a, p_b, color="rgba(0, 255, 0, 0.1)")
