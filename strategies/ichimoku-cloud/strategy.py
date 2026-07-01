# Ichimoku Cloud Strategy
from tg_scripting import *
import numpy as np

indicator("Ichimoku Cloud", overlay=True)

tenkan_len = input.int(9, "Tenkan Period", minval=2, maxval=50)
kijun_len = input.int(26, "Kijun Period", minval=5, maxval=100)
senkou_b_len = input.int(52, "Senkou B Period", minval=10, maxval=200)
show_labels = input.bool(True, "Show Labels")
show_levels = input.bool(True, "Show Entry/Stop/TP Levels")

tenkan, kijun, senkou_a, senkou_b, chikou = ta.ichimoku(high, low, close, tenkan_len, kijun_len, senkou_b_len)

cloud_top = np.maximum(senkou_a, senkou_b)
above_cloud = close[-1] > cloud_top[-1]
tk_cross = ta.crossover(tenkan, kijun)[-1]

long_cond = above_cloud and tk_cross
exit_cond = ta.crossunder(tenkan, kijun)[-1]

if long_cond:
    strategy.entry("Long", strategy.LONG)
if exit_cond:
    strategy.close("Long")

plot(tenkan, title="Tenkan-sen", color="blue")
plot(kijun, title="Kijun-sen", color="red")
p1 = plot(senkou_a, title="Senkou A", color="green")
p2 = plot(senkou_b, title="Senkou B", color="maroon")
fill(p1, p2, color="rgba(0,128,0,0.1)")

# --- Rich annotations ---
n = len(close)
cloud_top_arr = np.maximum(senkou_a, senkou_b)
cloud_bot_arr = np.minimum(senkou_a, senkou_b)
above_cloud_arr = close > cloud_top_arr
tk_cross_arr = ta.crossover(tenkan, kijun)
tk_under_arr = ta.crossunder(tenkan, kijun)
atr_ann = ta.atr(high, low, close, 14)
last_signal_idx = -100

for i in range(1, n):
    if i - last_signal_idx < 20:
        continue

    if above_cloud_arr[i] and tk_cross_arr[i]:
        last_signal_idx = i
        if show_labels:
            label.new(x=i, y=float(low[i]),
                      text="Cloud Breakout\nLONG",
                      style=label.style_label_up,
                      color="#00e676", textcolor="#000000", size="normal")
        if show_levels:
            entry_price = float(close[i])
            sl_price = float(cloud_bot_arr[i])
            tp_price = float(close[i] + (close[i] - cloud_bot_arr[i]) * 2)
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

    elif tk_under_arr[i]:
        last_signal_idx = i
        if show_labels:
            label.new(x=i, y=float(high[i]),
                      text="TK Cross Down\nEXIT",
                      style=label.style_label_down,
                      color="#ef5350", textcolor="#ffffff", size="normal")
