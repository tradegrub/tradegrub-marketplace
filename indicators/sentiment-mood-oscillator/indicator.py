from tg_scripting import *
import numpy as np

indicator("Sentiment Mood Oscillator", overlay=False)

rsi_len = input.int(14, "RSI Length", minval=5, maxval=50)
mfi_len = input.int(14, "MFI Length", minval=5, maxval=50)
roc_len = input.int(10, "ROC Length", minval=3, maxval=30)
smooth_len = input.int(5, "Smoothing Length", minval=1, maxval=20)
rsi_wt = input.int(40, "RSI Weight %", minval=0, maxval=100)
mfi_wt = input.int(30, "MFI Weight %", minval=0, maxval=100)
roc_wt = input.int(30, "ROC Weight %", minval=0, maxval=100)

src = np.array(close, dtype=float)
hi = np.array(high, dtype=float)
lo = np.array(low, dtype=float)
vol = np.array(volume, dtype=float)
n = len(src)

# RSI calculation
rsi_raw = np.array(ta.rsi(close, rsi_len), dtype=float)
rsi_norm = (rsi_raw - 50.0) * 2.0  # 0-100 -> -100 to +100

# MFI calculation
mfi_raw = np.array(ta.mfi(high, low, close, volume, mfi_len), dtype=float)
mfi_norm = (mfi_raw - 50.0) * 2.0  # 0-100 -> -100 to +100

# Rate of change as momentum component
roc = np.zeros(n)
for i in range(roc_len, n):
    prev = src[i - roc_len]
    if prev != 0:
        roc[i] = ((src[i] - prev) / prev) * 100.0
# Clamp ROC to -100..+100
roc = np.clip(roc, -100.0, 100.0)

# Weighted composite mood score
total_wt = max(rsi_wt + mfi_wt + roc_wt, 1)
mood_raw = (rsi_norm * rsi_wt + mfi_norm * mfi_wt + roc * roc_wt) / total_wt
mood_raw = np.clip(mood_raw, -100.0, 100.0)

# Smooth with EMA
mood = np.array(ta.ema(mood_raw.tolist(), smooth_len), dtype=float)

# Zone colors per bar
colors = []
for val in mood:
    if val > 60:
        colors.append("#00e676")    # euphoria - bright green
    elif val > 20:
        colors.append("#66bb6a")    # optimism - green
    elif val > -20:
        colors.append("#ffca28")    # neutral - yellow
    elif val > -60:
        colors.append("#ff7043")    # fear - orange-red
    else:
        colors.append("#ff1744")    # panic - red

# Zone reference lines
hline(60, title="Euphoria", color="#00e67680")
hline(20, title="Optimism", color="#66bb6a80")
hline(0, title="Neutral", color="#888888")
hline(-20, title="Fear", color="#ff704380")
hline(-60, title="Panic", color="#ff174480")

# Background fill for extreme zones
euphoria_bg = [True if m > 60 else False for m in mood]
panic_bg = [True if m < -60 else False for m in mood]
bgcolor(euphoria_bg, color="#00e67610")
bgcolor(panic_bg, color="#ff174410")

# Plot mood line
plot(mood.tolist(), title="Mood", color=colors)
