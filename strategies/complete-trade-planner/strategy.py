from tg_scripting import *
import numpy as np

indicator("Complete Trade Planner", overlay=True)

rsi_len = input.int(14, "RSI Length", minval=5, maxval=30)
ma_len = input.int(20, "MA Length", minval=10, maxval=50)
atr_len = input.int(14, "ATR Length", minval=5, maxval=30)
sl_mult = input.float(2.0, "Stop Loss ATR Mult", minval=1.0, maxval=5.0, step=0.5)
tp_mult = input.float(3.0, "Take Profit ATR Mult", minval=1.5, maxval=6.0, step=0.5)
trail_mult = input.float(1.5, "Trailing Stop ATR Mult", minval=0.5, maxval=3.0, step=0.5)
min_signals = input.int(2, "Min Signals for Entry", minval=1, maxval=3)

cl = np.array(close, dtype=float)
hi = np.array(high, dtype=float)
lo = np.array(low, dtype=float)
n = len(cl)

rsi_arr = np.array(ta.rsi(close, rsi_len), dtype=float)
rsi_arr = np.nan_to_num(rsi_arr, nan=50.0)

sma_arr = np.array(ta.sma(close, ma_len), dtype=float)
sma_arr = np.nan_to_num(sma_arr, nan=0.0)

macd_l, macd_s, macd_h = ta.macd(close, 12, 26, 9)
macd_hist = np.array(macd_h, dtype=float)
macd_hist = np.nan_to_num(macd_hist, nan=0.0)

atr_arr = np.array(ta.atr(high, low, close, atr_len), dtype=float)
atr_arr = np.nan_to_num(atr_arr, nan=1.0)

long_score = np.zeros(n, dtype=int)
short_score = np.zeros(n, dtype=int)
for i in range(ma_len, n):
    if rsi_arr[i] < 40:
        long_score[i] += 1
    if rsi_arr[i] > 60:
        short_score[i] += 1
    if cl[i] > sma_arr[i]:
        long_score[i] += 1
    if cl[i] < sma_arr[i]:
        short_score[i] += 1
    if macd_hist[i] > 0:
        long_score[i] += 1
    if macd_hist[i] < 0:
        short_score[i] += 1

in_long = False
in_short = False
entry_price = 0.0
trail_stop = 0.0

for i in range(ma_len, n):
    strategy.set_bar_index(i)
    if long_score[i] >= min_signals and not in_long:
        strategy.entry("Long", strategy.LONG)
        in_long = True
        in_short = False
        entry_price = float(cl[i])
        trail_stop = entry_price - atr_arr[i] * trail_mult
    elif short_score[i] >= min_signals and not in_short:
        strategy.entry("Short", strategy.SHORT)
        in_short = True
        in_long = False
        entry_price = float(cl[i])
        trail_stop = entry_price + atr_arr[i] * trail_mult

    if in_long:
        sl = entry_price - atr_arr[i] * sl_mult
        tp = entry_price + atr_arr[i] * tp_mult
        trail_stop = max(trail_stop, float(cl[i]) - atr_arr[i] * trail_mult)
        effective_stop = max(sl, trail_stop)
        strategy.exit("Long", stop=effective_stop, limit=tp)
        if cl[i] <= effective_stop or cl[i] >= tp:
            in_long = False

    if in_short:
        sl = entry_price + atr_arr[i] * sl_mult
        tp = entry_price - atr_arr[i] * tp_mult
        trail_stop = min(trail_stop, float(cl[i]) + atr_arr[i] * trail_mult)
        effective_stop = min(sl, trail_stop)
        strategy.exit("Short", stop=effective_stop, limit=tp)
        if cl[i] >= effective_stop or cl[i] <= tp:
            in_short = False

long_entry = long_score >= min_signals
short_entry = short_score >= min_signals
plotshape(long_entry.tolist(), title="Long Signal", style="triangleup", location="belowbar", color="#00e676", size="small")
plotshape(short_entry.tolist(), title="Short Signal", style="triangledown", location="abovebar", color="#ff1744", size="small")
plot(sma_arr.tolist(), title="Trend MA", color="#42a5f5", linewidth=1)

# --- Rich annotations: entry/stop/TP/trailing-stop levels ---
ann_in_long = False
ann_in_short = False
ann_entry_price = 0.0
ann_trail_stop = 0.0
last_signal_idx = -100
cooldown = 20
exit_bars = 30

for i in range(ma_len, n):
    if long_score[i] >= min_signals and not ann_in_long:
        ann_in_long = True
        ann_in_short = False
        ann_entry_price = float(cl[i])
        ann_trail_stop = ann_entry_price - atr_arr[i] * trail_mult
        if (i - last_signal_idx) > cooldown:
            last_signal_idx = i
            sl_price = ann_entry_price - atr_arr[i] * sl_mult
            tp_price = ann_entry_price + atr_arr[i] * tp_mult
            end_bar = min(i + exit_bars, n - 1)
            label.new(x=i, y=float(lo[i]), text="BUY",
                      style=label.style_label_up, color="#00e676",
                      textcolor="#000000", size="normal")
            line.new(x1=i, y1=ann_entry_price, x2=end_bar, y2=ann_entry_price,
                     color="#42a5f5", width=1, style=line.style_dashed)
            label.new(x=i + 2, y=ann_entry_price, text="Entry",
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
    elif short_score[i] >= min_signals and not ann_in_short:
        ann_in_short = True
        ann_in_long = False
        ann_entry_price = float(cl[i])
        ann_trail_stop = ann_entry_price + atr_arr[i] * trail_mult
        if (i - last_signal_idx) > cooldown:
            last_signal_idx = i
            sl_price = ann_entry_price + atr_arr[i] * sl_mult
            tp_price = ann_entry_price - atr_arr[i] * tp_mult
            end_bar = min(i + exit_bars, n - 1)
            label.new(x=i, y=float(hi[i]), text="SHORT",
                      style=label.style_label_down, color="#ef5350",
                      textcolor="#ffffff", size="normal")
            line.new(x1=i, y1=ann_entry_price, x2=end_bar, y2=ann_entry_price,
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

    if ann_in_long:
        sl = ann_entry_price - atr_arr[i] * sl_mult
        tp = ann_entry_price + atr_arr[i] * tp_mult
        ann_trail_stop = max(ann_trail_stop, float(cl[i]) - atr_arr[i] * trail_mult)
        effective_stop = max(sl, ann_trail_stop)
        line.new(x1=i, y1=effective_stop, x2=i + 1, y2=effective_stop,
                 color="#ff9800", width=2)
        if cl[i] <= effective_stop or cl[i] >= tp:
            ann_in_long = False
            label.new(x=i, y=float(hi[i]), text="EXIT",
                      style=label.style_label_down, color="#ef5350",
                      textcolor="#ffffff", size="normal")

    if ann_in_short:
        sl = ann_entry_price + atr_arr[i] * sl_mult
        tp = ann_entry_price - atr_arr[i] * tp_mult
        ann_trail_stop = min(ann_trail_stop, float(cl[i]) + atr_arr[i] * trail_mult)
        effective_stop = min(sl, ann_trail_stop)
        line.new(x1=i, y1=effective_stop, x2=i + 1, y2=effective_stop,
                 color="#ff9800", width=2)
        if cl[i] >= effective_stop or cl[i] <= tp:
            ann_in_short = False
            label.new(x=i, y=float(lo[i]), text="EXIT",
                      style=label.style_label_up, color="#ef5350",
                      textcolor="#ffffff", size="normal")
