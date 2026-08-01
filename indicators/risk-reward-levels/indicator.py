from tg_scripting import *
import numpy as np

indicator("Risk Reward Levels", overlay=True)

atr_len = input.int(14, "ATR Length", minval=5, maxval=50)
atr_mult = input.float(1.5, "ATR Multiplier", minval=0.5, maxval=5.0)
rr1 = input.float(1.5, "R:R Target 1", minval=0.5, maxval=10.0)
rr2 = input.float(2.5, "R:R Target 2", minval=0.5, maxval=10.0)
rr3 = input.float(3.5, "R:R Target 3", minval=0.5, maxval=10.0)
use_ema = input.bool(True, "Use EMA Bias")
ema_len = input.int(50, "EMA Length", minval=10, maxval=200)

atr = ta.atr(high, low, close, atr_len)
ema_val = ta.ema(close, ema_len)
risk_dist = atr * atr_mult

bullish = close > ema_val

entry = close.copy()
stop_long = entry - risk_dist
stop_short = entry + risk_dist

tp1_long = entry + risk_dist * rr1
tp2_long = entry + risk_dist * rr2
tp3_long = entry + risk_dist * rr3

tp1_short = entry - risk_dist * rr1
tp2_short = entry - risk_dist * rr2
tp3_short = entry - risk_dist * rr3

stop = np.where(bullish, stop_long, stop_short)
tp1 = np.where(bullish, tp1_long, tp1_short)
tp2 = np.where(bullish, tp2_long, tp2_short)
tp3 = np.where(bullish, tp3_long, tp3_short)

plot(entry, title="Entry", color="white", linewidth=2)
plot(stop, title="Stop Loss", color="red", linewidth=2)
plot(tp1, title="TP1", color="lime")
plot(tp2, title="TP2", color="green")
plot(tp3, title="TP3", color="teal")


plotshape(ta.crossover(close, ema_val), title="Bull Signal", shape="triangleup", location="belowbar", color="lime")
plotshape(ta.crossunder(close, ema_val), title="Bear Signal", shape="triangledown", location="abovebar", color="red")

# --- Rich annotations ---
show_labels = input.bool(True, "Show Labels")
show_levels = input.bool(True, "Show Levels")

cross_bull = ta.crossover(close, ema_val)
cross_bear = ta.crossunder(close, ema_val)

n = len(close)
last_label_idx = -100
cooldown = 20
hold_bars = 30

for i in range(ema_len, n):
    if not show_labels:
        break
    if (i - last_label_idx) <= cooldown:
        continue

    if cross_bull[i]:
        last_label_idx = i
        label.new(
            x=i, y=float(low[i]),
            text="LONG",
            style=label.style_label_up,
            color="#00e676",
            textcolor="#000000",
            size="normal"
        )
        if show_levels:
            end_bar = min(i + hold_bars, n - 1)
            sl = float(stop[i])
            t1 = float(tp1[i])
            t2 = float(tp2[i])
            t3 = float(tp3[i])
            entry_p = float(entry[i])

            line.new(x1=i, y1=sl, x2=end_bar, y2=sl,
                     color="#ef5350", width=1, style=line.style_dashed)
            label.new(x=i + 2, y=sl, text="Stop Loss",
                      style=label.style_label_left, color="rgba(239,83,80,0.2)",
                      textcolor="#ef5350", size="small")

            line.new(x1=i, y1=t1, x2=end_bar, y2=t1,
                     color="#00e676", width=1, style=line.style_dashed)
            label.new(x=i + 2, y=t1, text=f"TP1 ({rr1}:1)",
                      style=label.style_label_left, color="rgba(0,230,118,0.2)",
                      textcolor="#00e676", size="tiny")

            line.new(x1=i, y1=t2, x2=end_bar, y2=t2,
                     color="#00e676", width=1, style=line.style_dashed)
            label.new(x=i + 2, y=t2, text=f"TP2 ({rr2}:1)",
                      style=label.style_label_left, color="rgba(0,230,118,0.2)",
                      textcolor="#00e676", size="tiny")

            line.new(x1=i, y1=t3, x2=end_bar, y2=t3,
                     color="#00e676", width=1, style=line.style_dashed)
            label.new(x=i + 2, y=t3, text=f"TP3 ({rr3}:1)",
                      style=label.style_label_left, color="rgba(0,230,118,0.2)",
                      textcolor="#00e676", size="tiny")

            box.new(left=i, top=t3, right=end_bar, bottom=sl,
                    border_color="rgba(0,230,118,0.15)", bgcolor="rgba(0,230,118,0.03)")

    elif cross_bear[i]:
        last_label_idx = i
        label.new(
            x=i, y=float(high[i]),
            text="SHORT",
            style=label.style_label_down,
            color="#ef5350",
            textcolor="#ffffff",
            size="normal"
        )
        if show_levels:
            end_bar = min(i + hold_bars, n - 1)
            sl = float(stop[i])
            t1 = float(tp1[i])
            t2 = float(tp2[i])
            t3 = float(tp3[i])

            line.new(x1=i, y1=sl, x2=end_bar, y2=sl,
                     color="#ef5350", width=1, style=line.style_dashed)
            label.new(x=i + 2, y=sl, text="Stop Loss",
                      style=label.style_label_left, color="rgba(239,83,80,0.2)",
                      textcolor="#ef5350", size="small")

            line.new(x1=i, y1=t1, x2=end_bar, y2=t1,
                     color="#00e676", width=1, style=line.style_dashed)
            label.new(x=i + 2, y=t1, text=f"TP1 ({rr1}:1)",
                      style=label.style_label_left, color="rgba(0,230,118,0.2)",
                      textcolor="#00e676", size="tiny")

            line.new(x1=i, y1=t2, x2=end_bar, y2=t2,
                     color="#00e676", width=1, style=line.style_dashed)
            label.new(x=i + 2, y=t2, text=f"TP2 ({rr2}:1)",
                      style=label.style_label_left, color="rgba(0,230,118,0.2)",
                      textcolor="#00e676", size="tiny")

            line.new(x1=i, y1=t3, x2=end_bar, y2=t3,
                     color="#00e676", width=1, style=line.style_dashed)
            label.new(x=i + 2, y=t3, text=f"TP3 ({rr3}:1)",
                      style=label.style_label_left, color="rgba(0,230,118,0.2)",
                      textcolor="#00e676", size="tiny")

            box.new(left=i, top=sl, right=end_bar, bottom=t3,
                    border_color="rgba(239,83,80,0.15)", bgcolor="rgba(239,83,80,0.03)")
