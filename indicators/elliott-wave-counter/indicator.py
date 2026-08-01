from tg_scripting import *
import numpy as np

swing_length = input.int(10, "Swing Length", minval=3, maxval=50)

n = len(close)
wave_number = np.zeros(n)
pattern_score = np.zeros(n)

# Detect swing highs and lows using rolling window
swing_high = np.full(n, np.nan)
swing_low = np.full(n, np.nan)

for i in range(swing_length, n - swing_length):
    h = float(high[i])
    l = float(low[i])
    is_sh = True
    is_sl = True
    for j in range(1, swing_length + 1):
        if float(high[i - j]) >= h or float(high[i + j]) >= h:
            is_sh = False
        if float(low[i - j]) <= l or float(low[i + j]) <= l:
            is_sl = False
    if is_sh:
        swing_high[i] = h
    if is_sl:
        swing_low[i] = l

# Collect swing points in order
swing_indices = []
swing_prices = []
swing_types = []  # 1=high, -1=low

for i in range(n):
    if not np.isnan(swing_high[i]):
        swing_indices.append(i)
        swing_prices.append(float(swing_high[i]))
        swing_types.append(1)
    if not np.isnan(swing_low[i]):
        swing_indices.append(i)
        swing_prices.append(float(swing_low[i]))
        swing_types.append(-1)

# Alternate swings (remove consecutive same-type)
alt_idx = []
alt_price = []
alt_type = []
for k in range(len(swing_indices)):
    if len(alt_type) == 0 or swing_types[k] != alt_type[-1]:
        alt_idx.append(swing_indices[k])
        alt_price.append(swing_prices[k])
        alt_type.append(swing_types[k])
    else:
        if swing_types[k] == 1 and swing_prices[k] > alt_price[-1]:
            alt_idx[-1] = swing_indices[k]
            alt_price[-1] = swing_prices[k]
        elif swing_types[k] == -1 and swing_prices[k] < alt_price[-1]:
            alt_idx[-1] = swing_indices[k]
            alt_price[-1] = swing_prices[k]

# Look for 5-wave impulse patterns (low-high-low-high-low-high = 6 points)
for k in range(len(alt_idx) - 5):
    if alt_type[k] != -1:
        continue

    p = [alt_price[k + j] for j in range(6)]
    idx = [alt_idx[k + j] for j in range(6)]

    w1_start, w1_end = p[0], p[1]
    w2_end = p[2]
    w3_end = p[3]
    w4_end = p[4]
    w5_end = p[5]

    score = 0.0
    valid = True

    # Wave 2 doesn't retrace below wave 1 start
    if w2_end > w1_start:
        score += 25.0
    else:
        valid = False

    # Wave 3 is not the shortest
    w1_len = w1_end - w1_start
    w3_len = w3_end - w2_end
    w5_len = w5_end - w4_end
    if w3_len >= w1_len and w3_len >= w5_len:
        score += 25.0
    elif w3_len >= min(w1_len, w5_len):
        score += 10.0
    else:
        valid = False

    # Wave 4 doesn't overlap wave 1
    if w4_end > w1_end:
        score += 25.0
    else:
        valid = False

    # Wave 5 makes new high
    if w5_end > w3_end:
        score += 25.0
    elif w5_end > w1_end:
        score += 10.0

    if valid:
        for w in range(5):
            wi = idx[w]
            wave_number[wi] = w + 1
            pattern_score[wi] = score

plot(wave_number, title="Wave Number", color="#2196F3")
plot(pattern_score, title="Pattern Score", color="#FF9800")
hline(0, title="Zero", color="rgba(128,128,128,0.3)")
hline(75, title="High Quality", color="rgba(76,175,80,0.3)")

plotshape(wave_number == 5, title="Wave 5", style="diamond", location="top", color="#F44336")
plotshape(wave_number == 3, title="Wave 3", style="triangleup", location="bottom", color="#4CAF50")
