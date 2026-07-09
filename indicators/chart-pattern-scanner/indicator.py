from tg_scripting import *

indicator("Chart Pattern Scanner", overlay=True)

# --- Inputs ---
swing_len = input.int(5, "Swing Detection Length", minval=2, maxval=20)
lookback = input.int(100, "Pattern Lookback Bars", minval=30, maxval=300)
tolerance = input.float(0.04, "Pattern Tolerance (%)", minval=0.01, maxval=0.15)
min_swings = input.int(3, "Min Swings for Pattern", minval=2, maxval=10)

# --- Swing High/Low Detection ---
n = len(close)

high_diff = np.diff(high)
low_diff = np.diff(low)
high_sign = np.sign(high_diff)
low_sign = np.sign(low_diff)

high_sign_change = np.diff(high_sign)
low_sign_change = np.diff(low_sign)

swing_high_raw = np.pad(high_sign_change == -2, (1, 1), constant_values=False)
swing_low_raw = np.pad(low_sign_change == 2, (1, 1), constant_values=False)

swing_high_mask = np.zeros(n, dtype=bool)
swing_low_mask = np.zeros(n, dtype=bool)

for i in range(swing_len, n - swing_len):
    ws = max(0, i - swing_len)
    we = min(n, i + swing_len + 1)
    if swing_high_raw[i] and high[i] == np.max(high[ws:we]):
        swing_high_mask[i] = True
    if swing_low_raw[i] and low[i] == np.min(low[ws:we]):
        swing_low_mask[i] = True

sh_idx = np.where(swing_high_mask)[0]
sl_idx = np.where(swing_low_mask)[0]
sh_val = high[sh_idx]
sl_val = low[sl_idx]

# --- Pattern Detection ---
# Each detector returns list of (bar_index, score, name, trendline_points)
detections = []

# Double Top: two swing highs at similar levels
for i in range(len(sh_idx) - 1):
    pct_diff = abs(sh_val[i] - sh_val[i + 1]) / sh_val[i]
    if pct_diff < tolerance:
        gap = sh_idx[i + 1] - sh_idx[i]
        if 5 < gap < lookback:
            valley = np.min(low[sh_idx[i]:sh_idx[i + 1] + 1])
            depth = (sh_val[i] - valley) / sh_val[i]
            if depth > tolerance:
                score = -depth * 100
                pts = [(int(sh_idx[i]), float(sh_val[i])), (int(sh_idx[i + 1]), float(sh_val[i + 1]))]
                detections.append((int(sh_idx[i + 1]), score, "Double Top", pts, "#ef5350"))

# Double Bottom: two swing lows at similar levels
for i in range(len(sl_idx) - 1):
    pct_diff = abs(sl_val[i] - sl_val[i + 1]) / sl_val[i]
    if pct_diff < tolerance:
        gap = sl_idx[i + 1] - sl_idx[i]
        if 5 < gap < lookback:
            peak = np.max(high[sl_idx[i]:sl_idx[i + 1] + 1])
            depth = (peak - sl_val[i]) / sl_val[i]
            if depth > tolerance:
                score = depth * 100
                pts = [(int(sl_idx[i]), float(sl_val[i])), (int(sl_idx[i + 1]), float(sl_val[i + 1]))]
                detections.append((int(sl_idx[i + 1]), score, "Double Bottom", pts, "#00e676"))

# Head and Shoulders: three highs, middle tallest, shoulders similar
for i in range(len(sh_idx) - 2):
    ls, hd, rs = sh_val[i], sh_val[i + 1], sh_val[i + 2]
    if hd > ls and hd > rs:
        shoulder_diff = abs(ls - rs) / ls
        if shoulder_diff < tolerance * 3:
            prominence = (hd - (ls + rs) / 2) / hd
            if prominence > tolerance * 0.5:
                span = sh_idx[i + 2] - sh_idx[i]
                if span < lookback:
                    score = -prominence * 100
                    pts = [(int(sh_idx[i]), float(ls)), (int(sh_idx[i + 1]), float(hd)), (int(sh_idx[i + 2]), float(rs))]
                    detections.append((int(sh_idx[i + 2]), score, "Head & Shoulders", pts, "#ef5350"))

# Inverse Head and Shoulders: three lows, middle deepest, shoulders similar
for i in range(len(sl_idx) - 2):
    ls, hd, rs = sl_val[i], sl_val[i + 1], sl_val[i + 2]
    if hd < ls and hd < rs:
        shoulder_diff = abs(ls - rs) / ls
        if shoulder_diff < tolerance * 3:
            prominence = ((ls + rs) / 2 - hd) / hd
            if prominence > tolerance * 0.5:
                span = sl_idx[i + 2] - sl_idx[i]
                if span < lookback:
                    score = prominence * 100
                    pts = [(int(sl_idx[i]), float(ls)), (int(sl_idx[i + 1]), float(hd)), (int(sl_idx[i + 2]), float(rs))]
                    detections.append((int(sl_idx[i + 2]), score, "Inv H&S", pts, "#00e676"))

# Triangles and Wedges via rolling trendline regression
if len(sh_idx) >= min_swings and len(sl_idx) >= min_swings:
    window = min(5, len(sh_idx), len(sl_idx))
    for end in range(window, min(len(sh_idx), len(sl_idx)) + 1):
        r_sh = sh_idx[end - window:end]
        r_sl = sl_idx[end - window:end]
        r_sh_v = sh_val[end - window:end]
        r_sl_v = sl_val[end - window:end]
        if len(r_sh) < 2 or len(r_sl) < 2:
            continue
        span = max(r_sh[-1], r_sl[-1]) - min(r_sh[0], r_sl[0])
        if span < 10 or span > lookback:
            continue
        sh_slope = np.polyfit(r_sh.astype(float), r_sh_v, 1)[0]
        sl_slope = np.polyfit(r_sl.astype(float), r_sl_v, 1)[0]
        avg_p = np.mean(close[min(r_sh[0], r_sl[0]):max(r_sh[-1], r_sl[-1]) + 1])
        sh_s = sh_slope / avg_p
        sl_s = sl_slope / avg_p

        bar = int(max(r_sh[-1], r_sl[-1]))
        start = int(min(r_sh[0], r_sl[0]))
        sh_line_pts = [(start, float(np.polyval([sh_slope, np.polyfit(r_sh.astype(float), r_sh_v, 1)[1]], start))),
                       (bar, float(np.polyval([sh_slope, np.polyfit(r_sh.astype(float), r_sh_v, 1)[1]], bar)))]
        sl_line_pts = [(start, float(np.polyval([sl_slope, np.polyfit(r_sl.astype(float), r_sl_v, 1)[1]], start))),
                       (bar, float(np.polyval([sl_slope, np.polyfit(r_sl.astype(float), r_sl_v, 1)[1]], bar)))]

        thr = tolerance * 0.5
        if abs(sh_s) < thr and sl_s > thr:
            detections.append((bar, 50.0, "Asc Triangle", sh_line_pts + sl_line_pts, "#00e676"))
        elif abs(sl_s) < thr and sh_s < -thr:
            detections.append((bar, -50.0, "Desc Triangle", sh_line_pts + sl_line_pts, "#ef5350"))
        elif sh_s < -thr * 0.6 and sl_s < -thr * 0.6 and sh_s < sl_s:
            detections.append((bar, 40.0, "Falling Wedge", sh_line_pts + sl_line_pts, "#42a5f5"))
        elif sh_s > thr * 0.6 and sl_s > thr * 0.6 and sl_s > sh_s:
            detections.append((bar, -40.0, "Rising Wedge", sh_line_pts + sl_line_pts, "#ff9800"))

# --- Build output arrays ---
pattern_score = np.zeros(n)
for bar, score, name, pts, col in detections:
    if 0 <= bar < n:
        pattern_score[bar] += score

pattern_smooth = ta.sma(pattern_score, 3)

# --- Draw labels and trendlines for each detection ---
drawn_bars = set()
cooldown = 15

for bar, score, name, pts, col in sorted(detections, key=lambda x: abs(x[1]), reverse=True):
    if any(abs(bar - b) < cooldown for b in drawn_bars):
        continue
    drawn_bars.add(bar)

    is_bearish = score < 0
    y_pos = float(high[bar]) if is_bearish else float(low[bar])
    label.new(
        x=bar, y=y_pos,
        text=name,
        style=label.style_label_down if is_bearish else label.style_label_up,
        color=col,
        textcolor="#ffffff",
        size="normal"
    )

    if len(pts) == 2:
        line.new(x1=pts[0][0], y1=pts[0][1], x2=pts[1][0], y2=pts[1][1],
                 color=col, width=2, style="dashed")
    elif len(pts) == 3:
        line.new(x1=pts[0][0], y1=pts[0][1], x2=pts[1][0], y2=pts[1][1],
                 color=col, width=2, style="dashed")
        line.new(x1=pts[1][0], y1=pts[1][1], x2=pts[2][0], y2=pts[2][1],
                 color=col, width=2, style="dashed")
    elif len(pts) == 4:
        line.new(x1=pts[0][0], y1=pts[0][1], x2=pts[1][0], y2=pts[1][1],
                 color=col, width=2, style="dashed")
        line.new(x1=pts[2][0], y1=pts[2][1], x2=pts[3][0], y2=pts[3][1],
                 color=col, width=2, style="dashed")

# --- Plots ---
plotshape(swing_high_mask, title="Swing High", style="triangledown", location="abovebar", color="#EF5350", size="tiny")
plotshape(swing_low_mask, title="Swing Low", style="triangleup", location="belowbar", color="#26A69A", size="tiny")

bullish_mask = pattern_score > 0
bearish_mask = pattern_score < 0
plotshape(bullish_mask, title="Bullish Signal", style="diamond", location="belowbar", color="#00C853")
plotshape(bearish_mask, title="Bearish Signal", style="diamond", location="abovebar", color="#FF1744")

plot(pattern_smooth, title="Pattern Score", color="#7C4DFF")
hline(0.0, title="Zero", color="#78909C")

bgcolor(np.abs(pattern_score) > 30, color=np.where(pattern_score > 30, "rgba(0,200,83,0.08)", "rgba(255,23,68,0.08)"))
