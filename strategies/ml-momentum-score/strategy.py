from tg_scripting import *
import numpy as np

lookback = input.int(200, "Training Lookback", minval=50, maxval=500)
threshold = input.float(0.6, "Signal Threshold", minval=0.5, maxval=0.9)
rsi_period = input.int(14, "RSI Period", minval=5, maxval=50)
macd_fast = input.int(12, "MACD Fast", minval=5, maxval=30)
macd_slow = input.int(26, "MACD Slow", minval=15, maxval=50)

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

cur = score[-1]
if cur > threshold * 100:
    strategy.entry("ML Long", strategy.LONG)
if cur < (1 - threshold) * 100:
    strategy.close("ML Long")

plot(score, "ML Score", color="cyan")
hline(threshold * 100, "Buy Threshold", color="green", linestyle="dashed")
hline((1 - threshold) * 100, "Sell Threshold", color="red", linestyle="dashed")
