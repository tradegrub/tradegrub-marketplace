from tg_scripting import *
import numpy as np

min_period = input.int(5, "Min Period", minval=2, maxval=30)
max_period = input.int(60, "Max Period", minval=10, maxval=120)

src = close
n = len(src)

# Dominant cycle detection via autocorrelation
def detect_dominant_cycle(data, min_p, max_p):
    length = len(data)
    arr = np.array(data, dtype=float)
    mean = np.mean(arr)
    arr_centered = arr - mean
    var = np.sum(arr_centered ** 2)
    best_lag = (min_p + max_p) // 2
    best_corr = -1.0
    if var < 1e-10:
        return best_lag
    for lag in range(min_p, max_p + 1):
        if lag >= length:
            break
        corr = np.sum(arr_centered[:length - lag] * arr_centered[lag:]) / var
        if corr > best_corr:
            best_corr = corr
            best_lag = lag
    return best_lag

cycle = detect_dominant_cycle(src, min_period, max_period)

# Harmonic multiples
lengths = [max(2, cycle // 4), max(2, cycle // 2), max(2, cycle), max(2, cycle * 2)]

# Compute EMA for each harmonic length
def ema_calc(data, period):
    arr = np.array(data, dtype=float)
    result = np.empty_like(arr)
    alpha = 2.0 / (period + 1)
    result[0] = arr[0]
    for i in range(1, len(arr)):
        result[i] = alpha * arr[i] + (1.0 - alpha) * result[i - 1]
    return result

ribbon1 = ema_calc(src, lengths[0])
ribbon2 = ema_calc(src, lengths[1])
ribbon3 = ema_calc(src, lengths[2])
ribbon4 = ema_calc(src, lengths[3])

# Color by alignment: all ascending = bullish, all descending = bearish
aligned_bull = (ribbon1 > ribbon2) & (ribbon2 > ribbon3) & (ribbon3 > ribbon4)
aligned_bear = (ribbon1 < ribbon2) & (ribbon2 < ribbon3) & (ribbon3 < ribbon4)

color1 = np.where(aligned_bull, "#00e676", np.where(aligned_bear, "#ff1744", "#ffab40"))
color2 = np.where(aligned_bull, "#00c853", np.where(aligned_bear, "#d50000", "#ff9100"))
color3 = np.where(aligned_bull, "#00bfa5", np.where(aligned_bear, "#c62828", "#ff6d00"))
color4 = np.where(aligned_bull, "#009688", np.where(aligned_bear, "#b71c1c", "#e65100"))

plot(ribbon1, title="Ribbon 1 (Cycle/4)", color="#00e676")
plot(ribbon2, title="Ribbon 2 (Cycle/2)", color="#00c853")
plot(ribbon3, title="Ribbon 3 (Cycle)", color="#00bfa5")
plot(ribbon4, title="Ribbon 4 (Cycle*2)", color="#009688")
