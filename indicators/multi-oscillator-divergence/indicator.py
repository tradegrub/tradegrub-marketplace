from tg_scripting import *
import numpy as np

indicator("Multi-Oscillator Divergence", overlay=False)

rsi_len = input.int(14, "RSI Length", minval=2, maxval=50)
macd_fast = input.int(12, "MACD Fast", minval=2, maxval=50)
macd_slow = input.int(26, "MACD Slow", minval=5, maxval=100)
macd_sig = input.int(9, "MACD Signal", minval=2, maxval=50)
lookback = input.int(30, "Divergence Lookback", minval=10, maxval=100)
min_agree = input.int(2, "Min Oscillators Agreeing", minval=1, maxval=3)

cl = np.array(close, dtype=np.float64)
hi = np.array(high, dtype=np.float64)
lo = np.array(low, dtype=np.float64)
n = len(cl)

rsi = np.array(ta.rsi(close, rsi_len), dtype=np.float64)

ema_fast = np.array(ta.ema(close, macd_fast), dtype=np.float64)
ema_slow = np.array(ta.ema(close, macd_slow), dtype=np.float64)
macd_line = ema_fast - ema_slow
macd_signal = np.full(n, np.nan)
if n > macd_sig:
    k = 2.0 / (macd_sig + 1)
    macd_signal[macd_sig - 1] = np.mean(macd_line[:macd_sig])
    for i in range(macd_sig, n):
        macd_signal[i] = macd_line[i] * k + macd_signal[i - 1] * (1 - k)
macd_hist = macd_line - macd_signal

stoch_k = np.full(n, 50.0)
stoch_period = 14
for i in range(stoch_period - 1, n):
    hh = np.max(hi[i - stoch_period + 1:i + 1])
    ll = np.min(lo[i - stoch_period + 1:i + 1])
    if hh != ll:
        stoch_k[i] = 100.0 * (cl[i] - ll) / (hh - ll)

score = np.zeros(n)
bull_div = np.zeros(n, dtype=bool)
bear_div = np.zeros(n, dtype=bool)

for i in range(lookback, n):
    window_cl = cl[i - lookback:i + 1]
    window_rsi = rsi[i - lookback:i + 1]
    window_macd = macd_hist[i - lookback:i + 1]
    window_stoch = stoch_k[i - lookback:i + 1]

    price_low_idx = np.argmin(window_cl)
    price_high_idx = np.argmax(window_cl)

    bull_count = 0
    bear_count = 0

    if price_low_idx < lookback and cl[i] <= window_cl[price_low_idx] * 1.005:
        if not np.isnan(window_rsi[price_low_idx]) and rsi[i] > window_rsi[price_low_idx]:
            bull_count += 1
        if not np.isnan(window_macd[price_low_idx]) and macd_hist[i] > window_macd[price_low_idx]:
            bull_count += 1
        if stoch_k[i] > window_stoch[price_low_idx]:
            bull_count += 1

    if price_high_idx < lookback and cl[i] >= window_cl[price_high_idx] * 0.995:
        if not np.isnan(window_rsi[price_high_idx]) and rsi[i] < window_rsi[price_high_idx]:
            bear_count += 1
        if not np.isnan(window_macd[price_high_idx]) and macd_hist[i] < window_macd[price_high_idx]:
            bear_count += 1
        if stoch_k[i] < window_stoch[price_high_idx]:
            bear_count += 1

    if bull_count >= min_agree:
        bull_div[i] = True
        score[i] = bull_count
    elif bear_count >= min_agree:
        bear_div[i] = True
        score[i] = -bear_count

plot(score.tolist(), title="Divergence Score", color="#2196F3", linewidth=2)
hline(0, title="Zero", color="rgba(158,158,158,0.4)")
hline(2, title="Strong Bull", color="rgba(38,166,154,0.3)", linestyle="dashed")
hline(-2, title="Strong Bear", color="rgba(239,83,80,0.3)", linestyle="dashed")

plotshape(bull_div.tolist(), title="Bullish Divergence", style="triangleup",
          location="belowbar", color="#00e676", size="small")
plotshape(bear_div.tolist(), title="Bearish Divergence", style="triangledown",
          location="abovebar", color="#ff1744", size="small")
