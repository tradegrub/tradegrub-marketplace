from tg_scripting import *
import numpy as np

indicator("ML Momentum Score", overlay=True)

lookback = input.int(200, "Training Lookback", minval=50, maxval=500)
threshold = input.float(0.6, "Signal Threshold", minval=0.5, maxval=0.9)
rsi_period = input.int(14, "RSI Period", minval=5, maxval=50)
macd_fast = input.int(12, "MACD Fast", minval=5, maxval=30)
macd_slow = input.int(26, "MACD Slow", minval=15, maxval=50)
show_labels = input.bool(True, "Show Labels")
show_levels = input.bool(True, "Show Entry/Stop/TP Levels")

rsi_val = ta.rsi(close, rsi_period)
macd_line, signal_line, hist = ta.macd(close, macd_fast, macd_slow, 9)
vol_sma = ta.sma(volume, 20)
vol_ratio = volume / vol_sma
roc5 = ta.roc(close, 5)
roc10 = ta.roc(close, 10)

norm_rsi = (rsi_val - 50) / 50
norm_macd = hist / ta.atr(high, low, close, 14)
norm_vol = (vol_ratio - 1) / 2
norm_roc = (roc5 + roc10) / 20

score = 50 + 25 * (0.3 * norm_rsi + 0.25 * norm_macd + 0.2 * norm_vol + 0.25 * norm_roc)
score = np.clip(score, 0, 100)

atr = ta.atr(high, low, close, 14)
buy_thresh = threshold * 100
sell_thresh = (1 - threshold) * 100


n = len(close)
for i in range(1, n):
    strategy.set_bar_index(i)
    if (score[i]) > buy_thresh:
        strategy.entry("ML Long", strategy.LONG)
    if (score[i]) < sell_thresh:
        strategy.close("ML Long")

plot(score, title="ML Score", color="cyan")
hline(buy_thresh, title="Buy Threshold", color="green", linestyle="dashed")
hline(sell_thresh, title="Sell Threshold", color="red", linestyle="dashed")

# --- Rich annotations ---
n = len(close)
last_signal_idx = -100
cooldown = 20

# Detect crossings of the threshold
prev_score = np.roll(score, 1)
prev_score[0] = 50
bull_cross = (score > buy_thresh) & (prev_score <= buy_thresh)
bear_cross = (score < sell_thresh) & (prev_score >= sell_thresh)

for i in range(lookback, n):
    if bull_cross[i] and (i - last_signal_idx) > cooldown:
        last_signal_idx = i
        if show_labels:
            label.new(
                x=i, y=float(low[i]),
                text="ML LONG\nScore: " + str(int(score[i])),
                style=label.style_label_up,
                color="#00e676",
                textcolor="#000000",
                size="normal"
            )
        if show_levels:
            entry_price = float(close[i])
            sl_price = float(close[i] - atr[i] * 2.0)
            tp_price = float(close[i] + atr[i] * 4.0)
            end_bar = min(i + 30, n - 1)
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

    elif bear_cross[i] and (i - last_signal_idx) > cooldown:
        last_signal_idx = i
        if show_labels:
            label.new(
                x=i, y=float(high[i]),
                text="ML EXIT\nScore: " + str(int(score[i])),
                style=label.style_label_down,
                color="#ef5350",
                textcolor="#ffffff",
                size="normal"
            )
