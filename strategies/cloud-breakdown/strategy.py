from tg_scripting import *
import numpy as np

indicator("Cloud Breakdown", overlay=True)

tenkan_len = input.int(9, "Tenkan Period", minval=5, maxval=30)
kijun_len = input.int(26, "Kijun Period", minval=15, maxval=60)
senkou_b_len = input.int(52, "Senkou B Period", minval=30, maxval=120)
displacement = input.int(26, "Displacement", minval=10, maxval=52)
atr_len = input.int(14, "ATR Period", minval=5, maxval=30)
atr_mult = input.float(2.0, "ATR Stop Multiplier", minval=0.5, maxval=5.0)
use_chikou_confirm = input.bool(True, "Chikou Confirmation")
risk_pct = input.float(1.0, "Risk Per Trade %", minval=0.1, maxval=5.0)
show_labels = input.bool(True, "Show Labels")
show_levels = input.bool(True, "Show Entry/Stop/TP Levels")

tenkan = (ta.highest(high, tenkan_len) + ta.lowest(low, tenkan_len)) / 2
kijun = (ta.highest(high, kijun_len) + ta.lowest(low, kijun_len)) / 2
senkou_a = (tenkan + kijun) / 2
senkou_b = (ta.highest(high, senkou_b_len) + ta.lowest(low, senkou_b_len)) / 2

cloud_top = np.maximum(senkou_a, senkou_b)
cloud_bot = np.minimum(senkou_a, senkou_b)

atr = ta.atr(high, low, close, atr_len)
tk_cross_bear = ta.crossunder(tenkan, kijun)
price_below_cloud = close < cloud_bot

chikou = np.roll(close, displacement)
chikou_below = chikou < cloud_bot

if use_chikou_confirm:
    entry_signal = price_below_cloud & tk_cross_bear & chikou_below
else:
    entry_signal = price_below_cloud & tk_cross_bear

exit_signal = ta.crossover(tenkan, kijun) | (close > cloud_top)

plot(tenkan, title="Tenkan", color="blue")
plot(kijun, title="Kijun", color="red")
plot(senkou_a, title="Senkou A", color="green")
plot(senkou_b, title="Senkou B", color="red")
bgcolor(price_below_cloud, color="rgba(255,0,0,0.05)")

n = len(close)
last_signal_idx = -100
cooldown = 20
exit_bars = 30
cloud_label_placed = False

for i in range(len(close)):
    strategy.set_bar_index(i)
    if entry_signal[i]:
        strategy.entry("Short", strategy.SHORT)

        if (i - last_signal_idx) > cooldown:
            last_signal_idx = i
            if show_labels:
                label.new(x=i, y=float(high[i]), text="SHORT\nCloud Breakdown",
                          style=label.style_label_down, color="#ef5350",
                          textcolor="#ffffff", size="normal")
            if show_levels:
                entry_price = float(close[i])
                sl_price = float(cloud_top[i] + atr[i] * 0.5)
                tp_price = float(close[i] - atr[i] * atr_mult)
                end_bar = min(i + exit_bars, n - 1)
                line.new(x1=i, y1=entry_price, x2=end_bar, y2=entry_price,
                         color="#42a5f5", width=1, style=line.style_dashed)
                label.new(x=i + 2, y=entry_price, text="Entry",
                          style=label.style_label_left, color="rgba(66,165,245,0.2)",
                          textcolor="#42a5f5", size="small")
                line.new(x1=i, y1=sl_price, x2=end_bar, y2=sl_price,
                         color="#ef5350", width=1, style=line.style_dashed)
                label.new(x=i + 2, y=sl_price, text="Stop (Above Cloud)",
                          style=label.style_label_left, color="rgba(239,83,80,0.2)",
                          textcolor="#ef5350", size="small")
                line.new(x1=i, y1=tp_price, x2=end_bar, y2=tp_price,
                         color="#00e676", width=1, style=line.style_dashed)
                label.new(x=i + 2, y=tp_price, text="Take Profit",
                          style=label.style_label_left, color="rgba(0,230,118,0.2)",
                          textcolor="#00e676", size="small")
                box.new(left=i, top=sl_price, right=end_bar, bottom=tp_price,
                        border_color="rgba(239,83,80,0.15)", bgcolor="rgba(239,83,80,0.03)")

    elif exit_signal[i]:
        strategy.close("Short")
        if show_labels and (i - last_signal_idx) > cooldown // 2:
            label.new(x=i, y=float(low[i]), text="EXIT\nTK Cross Up",
                      style=label.style_label_up, color="rgba(0,230,118,0.5)",
                      textcolor="#00e676", size="small")

    # Label the cloud once
    if show_labels and not cloud_label_placed and price_below_cloud[i]:
        cloud_label_placed = True
        label.new(x=i, y=float(cloud_top[i]), text="Ichimoku Cloud",
                  style=label.style_label_down, color="rgba(136,136,136,0.3)",
                  textcolor="#888888", size="normal")
