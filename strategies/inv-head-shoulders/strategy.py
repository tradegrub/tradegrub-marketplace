from tg_scripting import *
import numpy as np

strategy("Inv Head Shoulders", overlay=True)

lookback = input.int(50, "Lookback Period", minval=20, maxval=200)
shoulder_tol = input.float(2.0, "Shoulder Tolerance %", minval=0.5, maxval=10.0)
min_depth = input.float(3.0, "Min Head Depth %", minval=1.0, maxval=15.0)
vol_confirm = input.bool(True, "Volume Confirmation")
atr_mult = input.float(1.5, "Stop ATR Multiple", minval=0.5, maxval=4.0)
target_mult = input.float(2.0, "Target Multiple", minval=1.0, maxval=5.0)
vol_sma_len = input.int(20, "Volume SMA Length", minval=5, maxval=50)
show_labels = input.bool(True, "Show Labels")
show_levels = input.bool(True, "Show Entry/Stop/TP Levels")

atr = ta.atr(high, low, close, 14)
vol_sma = ta.sma(volume, vol_sma_len)

left_shoulder_low = ta.lowest(low, lookback // 3)
head_low = ta.lowest(low, lookback)
right_shoulder_low = ta.lowest(low, lookback // 3)

neckline = ta.highest(high, lookback // 2)
neckline_sma = ta.sma(neckline, 5)

head_deeper = (head_low < left_shoulder_low * (1 - min_depth / 100))
shoulders_match = abs(left_shoulder_low - right_shoulder_low) / left_shoulder_low * 100 < shoulder_tol
price_break = ta.crossover(close, neckline_sma)
vol_ok = ~vol_confirm | (volume > vol_sma * 1.2)

pattern_valid = head_deeper & shoulders_match & price_break & vol_ok

pattern_height = neckline_sma - head_low

n = len(close)
last_signal_idx = -100
exit_bars = 30

for i in range(len(close)):
    if pattern_valid[i]:
        stop_price = close[i] - atr[i] * atr_mult
        take_price = close[i] + pattern_height[i] * target_mult
        strategy.entry("Long", strategy.LONG)

        if (i - last_signal_idx) > lookback // 2:
            last_signal_idx = i

            if show_labels:
                label.new(
                    x=i, y=float(low[i]),
                    text="IH&S\nBREAKOUT",
                    style=label.style_label_up,
                    color="#00e676",
                    textcolor="#000000",
                    size="normal"
                )
                label.new(
                    x=i, y=float(head_low[i]),
                    text="Head",
                    style=label.style_label_up,
                    color="rgba(239,83,80,0.2)",
                    textcolor="#ef5350",
                    size="small"
                )
                label.new(
                    x=i, y=float(neckline_sma[i]),
                    text="Neckline",
                    style=label.style_label_down,
                    color="rgba(66,165,245,0.2)",
                    textcolor="#42a5f5",
                    size="small"
                )

            if show_levels:
                entry_price = float(close[i])
                sl_price = float(stop_price)
                tp_price = float(take_price)
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

    elif close[i] < head_low[i]:
        strategy.close("Long")

plot(neckline_sma, title="Neckline", color="blue")
plot(head_low, title="Head Low", color="red")
plotshape(pattern_valid, title="IHS Signal", shape="triangleup", location="belowbar", color="green")
bgcolor(pattern_valid, color="rgba(0,200,0,0.1)")
