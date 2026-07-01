from tg_scripting import *

pivot_len = input.int(5, "Pivot Length", minval=2, maxval=20)
min_steps = input.int(3, "Min Steps", minval=2, maxval=10)
consistency_thresh = input.float(0.5, "Consistency Threshold")
atr_len = input.int(14, "ATR Length", minval=5, maxval=50)
step_line_len = input.int(20, "Step Line Length", minval=5, maxval=50)

atr_val = ta.atr(high, low, close, atr_len)
sma_val = ta.sma(close, pivot_len * 2)

is_pivot_high = (high == ta.highest(high, pivot_len * 2 + 1))
is_pivot_low = (low == ta.lowest(low, pivot_len * 2 + 1))

prev_swing_high = 0.0
prev_swing_low = 0.0
curr_swing_high = 0.0
curr_swing_low = 0.0

up_step_sizes = []
dn_step_sizes = []
up_step_count = 0
dn_step_count = 0

cur_ph = bool(is_pivot_high[0])
cur_pl = bool(is_pivot_low[0])
cur_high = float(high[0])
cur_low = float(low[0])
cur_close = float(close[0])
cur_sma = float(sma_val[0])

if cur_ph:
    prev_swing_high = curr_swing_high
    curr_swing_high = cur_high
    if prev_swing_high > 0 and curr_swing_high < prev_swing_high:
        step_size = prev_swing_high - curr_swing_high
        if len(dn_step_sizes) >= 10:
            dn_step_sizes = dn_step_sizes[1:]
        dn_step_sizes.append(step_size)
        dn_step_count = dn_step_count + 1
    elif prev_swing_high > 0 and curr_swing_high > prev_swing_high:
        dn_step_sizes = []
        dn_step_count = 0

if cur_pl:
    prev_swing_low = curr_swing_low
    curr_swing_low = cur_low
    if prev_swing_low > 0 and curr_swing_low > prev_swing_low:
        step_size = curr_swing_low - prev_swing_low
        if len(up_step_sizes) >= 10:
            up_step_sizes = up_step_sizes[1:]
        up_step_sizes.append(step_size)
        up_step_count = up_step_count + 1
    elif prev_swing_low > 0 and curr_swing_low < prev_swing_low:
        up_step_sizes = []
        up_step_count = 0

up_consistency = 1.0
if len(up_step_sizes) >= 2:
    mean_up = sum(up_step_sizes) / len(up_step_sizes)
    if mean_up > 0:
        var_up = sum((s - mean_up) ** 2 for s in up_step_sizes) / len(up_step_sizes)
        up_consistency = (var_up ** 0.5) / mean_up

dn_consistency = 1.0
if len(dn_step_sizes) >= 2:
    mean_dn = sum(dn_step_sizes) / len(dn_step_sizes)
    if mean_dn > 0:
        var_dn = sum((s - mean_dn) ** 2 for s in dn_step_sizes) / len(dn_step_sizes)
        dn_consistency = (var_dn ** 0.5) / mean_dn

is_uptrend = cur_close > cur_sma
is_downtrend = cur_close < cur_sma

up_score = 0.0
if len(up_step_sizes) >= 2:
    count_score = min(up_step_count, 8) / 8.0 * 40.0
    consist_score = max(0, 1.0 - up_consistency) * 40.0
    trend_score = 20.0 if is_uptrend else 0.0
    up_score = count_score + consist_score + trend_score

dn_score = 0.0
if len(dn_step_sizes) >= 2:
    count_score = min(dn_step_count, 8) / 8.0 * 40.0
    consist_score = max(0, 1.0 - dn_consistency) * 40.0
    trend_score = 20.0 if is_downtrend else 0.0
    dn_score = count_score + consist_score + trend_score

stair_score = min(max(up_score, dn_score), 100.0)

up_stair_active = (up_step_count >= min_steps) and (up_consistency < consistency_thresh) and is_uptrend
dn_stair_active = (dn_step_count >= min_steps) and (dn_consistency < consistency_thresh) and is_downtrend

new_up_step = cur_pl and (prev_swing_low > 0) and (curr_swing_low > prev_swing_low) and (up_step_count >= min_steps) and (up_consistency < consistency_thresh)
new_dn_step = cur_ph and (prev_swing_high > 0) and (curr_swing_high < prev_swing_high) and (dn_step_count >= min_steps) and (dn_consistency < consistency_thresh)

plot(stair_score, title="Stair Score", color="#4fc3f7")
hline(60, title="Threshold", color="#555555")

if up_stair_active:
    bgcolor(1, color="rgba(76, 175, 80, 0.08)")

if dn_stair_active:
    bgcolor(1, color="rgba(244, 67, 54, 0.08)")

if new_up_step:
    plotshape(1, title="Up Step", style="triangleup", location="belowbar", color="#4caf50")

if new_dn_step:
    plotshape(1, title="Dn Step", style="triangledown", location="abovebar", color="#f44336")

if new_up_step:
    line.new(x1=0, y1=curr_swing_low, x2=step_line_len, y2=curr_swing_low, color="#4caf50")

if new_dn_step:
    line.new(x1=0, y1=curr_swing_high, x2=step_line_len, y2=curr_swing_high, color="#f44336")
