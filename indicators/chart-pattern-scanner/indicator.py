from tg_scripting import *

indicator("Chart Pattern Scanner", overlay=True, max_labels_count=500, max_lines_count=500)

# --- Inputs ---
swing_len = input.int(5, "Swing Detection Length", minval=2, maxval=20)
lookback = input.int(100, "Pattern Lookback Bars", minval=30, maxval=300)
tolerance = input.float(0.04, "Pattern Tolerance (%)", minval=0.01, maxval=0.15)
min_swings = input.int(3, "Min Swings for Pattern", minval=2, maxval=10)
rich_annotations = input.bool(True, "Rich Annotations")

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

# --- Colors (muted for cleaner chart) ---
COL_BEAR = "rgba(239,83,80,0.75)"
COL_BULL = "rgba(0,230,118,0.75)"
COL_BEAR_SOLID = "#ef5350"
COL_BULL_SOLID = "#00e676"
COL_NECK = "rgba(66,165,245,0.55)"
COL_LEVEL = "rgba(255,152,0,0.7)"
COL_WEDGE = "rgba(66,165,245,0.7)"
COL_LABEL = "rgba(255,255,255,0.65)"

def _find_neckline_lows(start_bar, end_bar):
    mask = (sl_idx >= start_bar) & (sl_idx <= end_bar)
    idxs = sl_idx[mask]
    vals = sl_val[mask]
    if len(idxs) >= 2:
        order = np.argsort(vals)
        return [(int(idxs[order[0]]), float(vals[order[0]])),
                (int(idxs[order[1]]), float(vals[order[1]]))]
    elif len(idxs) == 1:
        return [(int(idxs[0]), float(vals[0]))]
    return []

def _find_neckline_highs(start_bar, end_bar):
    mask = (sh_idx >= start_bar) & (sh_idx <= end_bar)
    idxs = sh_idx[mask]
    vals = sh_val[mask]
    if len(idxs) >= 2:
        order = np.argsort(-vals)
        return [(int(idxs[order[0]]), float(vals[order[0]])),
                (int(idxs[order[1]]), float(vals[order[1]]))]
    elif len(idxs) == 1:
        return [(int(idxs[0]), float(vals[0]))]
    return []

def _detect_breakdown(neckline_y, after_bar, direction, scan_bars=20):
    end = min(after_bar + scan_bars, n)
    for b in range(after_bar + 1, end):
        if direction == "down" and close[b] < neckline_y:
            return b
        elif direction == "up" and close[b] > neckline_y:
            return b
    return -1

# --- Pattern Detection ---
detections = []

# Double Top
for i in range(len(sh_idx) - 1):
    pct_diff = abs(sh_val[i] - sh_val[i + 1]) / sh_val[i]
    if pct_diff < tolerance:
        gap = sh_idx[i + 1] - sh_idx[i]
        if 5 < gap < lookback:
            valley_idx = int(sh_idx[i]) + int(np.argmin(low[sh_idx[i]:sh_idx[i + 1] + 1]))
            valley = float(low[valley_idx])
            depth = (sh_val[i] - valley) / sh_val[i]
            if depth > tolerance:
                score = -depth * 100
                detections.append({
                    "bar": int(sh_idx[i + 1]), "score": score, "name": "Double Top", "type": "double_top",
                    "p1": (int(sh_idx[i]), float(sh_val[i])),
                    "p2": (int(sh_idx[i + 1]), float(sh_val[i + 1])),
                    "neckline_y": valley, "neckline_bar": valley_idx,
                    "color": COL_BEAR,
                })

# Double Bottom
for i in range(len(sl_idx) - 1):
    pct_diff = abs(sl_val[i] - sl_val[i + 1]) / sl_val[i]
    if pct_diff < tolerance:
        gap = sl_idx[i + 1] - sl_idx[i]
        if 5 < gap < lookback:
            peak_idx = int(sl_idx[i]) + int(np.argmax(high[sl_idx[i]:sl_idx[i + 1] + 1]))
            peak = float(high[peak_idx])
            depth = (peak - sl_val[i]) / sl_val[i]
            if depth > tolerance:
                score = depth * 100
                detections.append({
                    "bar": int(sl_idx[i + 1]), "score": score, "name": "Double Bottom", "type": "double_bottom",
                    "p1": (int(sl_idx[i]), float(sl_val[i])),
                    "p2": (int(sl_idx[i + 1]), float(sl_val[i + 1])),
                    "neckline_y": peak, "neckline_bar": peak_idx,
                    "color": COL_BULL,
                })

# Head and Shoulders
for i in range(len(sh_idx) - 2):
    ls, hd, rs = float(sh_val[i]), float(sh_val[i + 1]), float(sh_val[i + 2])
    if hd > ls and hd > rs:
        shoulder_diff = abs(ls - rs) / ls
        if shoulder_diff < tolerance * 3:
            prominence = (hd - (ls + rs) / 2) / hd
            if prominence > tolerance * 0.5:
                span = sh_idx[i + 2] - sh_idx[i]
                if span < lookback:
                    neck_pts = _find_neckline_lows(int(sh_idx[i]), int(sh_idx[i + 2]))
                    neck_y = neck_pts[0][1] if neck_pts else (ls + rs) / 2 - (hd - (ls + rs) / 2)
                    score = -prominence * 100
                    detections.append({
                        "bar": int(sh_idx[i + 2]), "score": score, "name": "Head & Shoulders", "type": "hs",
                        "s1": (int(sh_idx[i]), ls), "head": (int(sh_idx[i + 1]), hd), "s2": (int(sh_idx[i + 2]), rs),
                        "neckline_pts": neck_pts, "neckline_y": neck_y,
                        "color": COL_BEAR,
                    })

# Inverse Head and Shoulders
for i in range(len(sl_idx) - 2):
    ls, hd, rs = float(sl_val[i]), float(sl_val[i + 1]), float(sl_val[i + 2])
    if hd < ls and hd < rs:
        shoulder_diff = abs(ls - rs) / ls
        if shoulder_diff < tolerance * 3:
            prominence = ((ls + rs) / 2 - hd) / hd
            if prominence > tolerance * 0.5:
                span = sl_idx[i + 2] - sl_idx[i]
                if span < lookback:
                    neck_pts = _find_neckline_highs(int(sl_idx[i]), int(sl_idx[i + 2]))
                    neck_y = neck_pts[0][1] if neck_pts else (ls + rs) / 2 + ((ls + rs) / 2 - hd)
                    score = prominence * 100
                    detections.append({
                        "bar": int(sl_idx[i + 2]), "score": score, "name": "Inv Head & Shoulders", "type": "ihs",
                        "s1": (int(sl_idx[i]), ls), "head": (int(sl_idx[i + 1]), hd), "s2": (int(sl_idx[i + 2]), rs),
                        "neckline_pts": neck_pts, "neckline_y": neck_y,
                        "color": COL_BULL,
                    })

# Triangles and Wedges
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
        sh_fit = np.polyfit(r_sh.astype(float), r_sh_v, 1)
        sl_fit = np.polyfit(r_sl.astype(float), r_sl_v, 1)
        avg_p = np.mean(close[min(r_sh[0], r_sl[0]):max(r_sh[-1], r_sl[-1]) + 1])
        sh_s = sh_fit[0] / avg_p
        sl_s = sl_fit[0] / avg_p

        bar = int(max(r_sh[-1], r_sl[-1]))
        start = int(min(r_sh[0], r_sl[0]))
        res_start = float(np.polyval(sh_fit, start))
        res_end = float(np.polyval(sh_fit, bar))
        sup_start = float(np.polyval(sl_fit, start))
        sup_end = float(np.polyval(sl_fit, bar))

        thr = tolerance * 0.5
        tri_name = None
        tri_col = None
        tri_score = 0
        if abs(sh_s) < thr and sl_s > thr:
            tri_name, tri_col, tri_score = "Ascending Triangle", COL_BULL, 50.0
        elif abs(sl_s) < thr and sh_s < -thr:
            tri_name, tri_col, tri_score = "Descending Triangle", COL_BEAR, -50.0
        elif sh_s < -thr * 0.6 and sl_s < -thr * 0.6 and sh_s < sl_s:
            tri_name, tri_col, tri_score = "Falling Wedge", COL_WEDGE, 40.0
        elif sh_s > thr * 0.6 and sl_s > thr * 0.6 and sl_s > sh_s:
            tri_name, tri_col, tri_score = "Rising Wedge", COL_LEVEL, -40.0

        if tri_name:
            detections.append({
                "bar": bar, "score": tri_score, "name": tri_name, "type": "triangle",
                "res_line": (start, res_start, bar, res_end),
                "sup_line": (start, sup_start, bar, sup_end),
                "color": tri_col,
            })

# --- Build output arrays ---
pattern_score = np.zeros(n)
for det in detections:
    b = det["bar"]
    if 0 <= b < n:
        pattern_score[b] += det["score"]

pattern_smooth = ta.sma(pattern_score, 3)

# --- Filter and deduplicate ---
drawn_bars = set()
cooldown = 15
display_list = []

for det in sorted(detections, key=lambda x: abs(x["score"]), reverse=True):
    bar = det["bar"]
    if any(abs(bar - b) < cooldown for b in drawn_bars):
        continue
    drawn_bars.add(bar)
    display_list.append(det)

# --- Legend table (top-left) ---
if display_list:
    legend = table.new(
        position=table.position.top_left,
        columns=3, rows=min(len(display_list), 10) + 1,
        bgcolor="rgba(19,23,34,0.85)",
        border_width=0, frame_width=1, frame_color="rgba(255,255,255,0.08)"
    )
    table.cell(legend, 0, 0, text="Pattern", text_color="rgba(255,255,255,0.5)", text_size="tiny", text_halign="left")
    table.cell(legend, 1, 0, text="Score", text_color="rgba(255,255,255,0.5)", text_size="tiny")
    table.cell(legend, 2, 0, text="Bias", text_color="rgba(255,255,255,0.5)", text_size="tiny")

    for row_i, det in enumerate(display_list[:10]):
        r = row_i + 1
        is_bear = det["score"] < 0
        sc_col = COL_BEAR_SOLID if is_bear else COL_BULL_SOLID
        bias_text = "Bearish" if is_bear else "Bullish"
        bd = ""
        if det["type"] in ("double_top", "hs"):
            bd_bar = _detect_breakdown(det["neckline_y"], det["bar"], "down")
            if bd_bar > 0:
                bias_text = "Breakdown"
        elif det["type"] in ("double_bottom", "ihs"):
            bd_bar = _detect_breakdown(det["neckline_y"], det["bar"], "up")
            if bd_bar > 0:
                bias_text = "Breakout"

        table.cell(legend, 0, r, text=det["name"], text_color="#d1d4dc", text_size="tiny", text_halign="left")
        table.cell(legend, 1, r, text=str(int(abs(det["score"]))), text_color=sc_col, text_size="tiny")
        table.cell(legend, 2, r, text=bias_text, text_color=sc_col, text_size="tiny")

# --- Draw on-chart annotations ---
for det in display_list:
    bar = det["bar"]
    col = det["color"]
    ptype = det["type"]
    is_bearish = det["score"] < 0

    if not rich_annotations:
        continue

    if ptype == "double_top":
        p1, p2 = det["p1"], det["p2"]
        neck_y = det["neckline_y"]
        label.new(x=p1[0], y=p1[1], text="P1", style=label.style_none,
                  color="rgba(0,0,0,0)", textcolor=COL_LABEL, size="tiny")
        label.new(x=p2[0], y=p2[1], text="P2", style=label.style_none,
                  color="rgba(0,0,0,0)", textcolor=COL_LABEL, size="tiny")
        line.new(x1=p1[0], y1=p1[1], x2=p2[0], y2=p2[1], color=col, width=1, style="dashed")
        line.new(x1=p1[0], y1=neck_y, x2=min(p2[0] + 10, n - 1), y2=neck_y,
                 color=COL_NECK, width=1, style="dotted")

    elif ptype == "double_bottom":
        p1, p2 = det["p1"], det["p2"]
        neck_y = det["neckline_y"]
        label.new(x=p1[0], y=p1[1], text="P1", style=label.style_none,
                  color="rgba(0,0,0,0)", textcolor=COL_LABEL, size="tiny")
        label.new(x=p2[0], y=p2[1], text="P2", style=label.style_none,
                  color="rgba(0,0,0,0)", textcolor=COL_LABEL, size="tiny")
        line.new(x1=p1[0], y1=p1[1], x2=p2[0], y2=p2[1], color=col, width=1, style="dashed")
        line.new(x1=p1[0], y1=neck_y, x2=min(p2[0] + 10, n - 1), y2=neck_y,
                 color=COL_NECK, width=1, style="dotted")

    elif ptype == "hs":
        s1, head, s2 = det["s1"], det["head"], det["s2"]
        neck_pts = det.get("neckline_pts", [])
        neck_y = det["neckline_y"]
        label.new(x=s1[0], y=s1[1], text="S1", style=label.style_none,
                  color="rgba(0,0,0,0)", textcolor=COL_LABEL, size="tiny")
        label.new(x=head[0], y=head[1], text="H", style=label.style_none,
                  color="rgba(0,0,0,0)", textcolor=COL_LABEL, size="tiny")
        label.new(x=s2[0], y=s2[1], text="S2", style=label.style_none,
                  color="rgba(0,0,0,0)", textcolor=COL_LABEL, size="tiny")
        line.new(x1=s1[0], y1=s1[1], x2=head[0], y2=head[1], color=col, width=1, style="dashed")
        line.new(x1=head[0], y1=head[1], x2=s2[0], y2=s2[1], color=col, width=1, style="dashed")
        if len(neck_pts) >= 2:
            nx1, ny1 = neck_pts[0]
            nx2, ny2 = neck_pts[1]
            ext_bar = min(s2[0] + 10, n - 1)
            if nx1 != nx2:
                slope = (ny2 - ny1) / (nx2 - nx1)
                ext_y = ny1 + slope * (ext_bar - nx1)
            else:
                ext_y = ny1
            line.new(x1=nx1, y1=ny1, x2=ext_bar, y2=float(ext_y), color=COL_NECK, width=1, style="dotted")
        else:
            line.new(x1=s1[0], y1=neck_y, x2=min(s2[0] + 10, n - 1), y2=neck_y,
                     color=COL_NECK, width=1, style="dotted")

    elif ptype == "ihs":
        s1, head, s2 = det["s1"], det["head"], det["s2"]
        neck_pts = det.get("neckline_pts", [])
        neck_y = det["neckline_y"]
        label.new(x=s1[0], y=s1[1], text="S1", style=label.style_none,
                  color="rgba(0,0,0,0)", textcolor=COL_LABEL, size="tiny")
        label.new(x=head[0], y=head[1], text="H", style=label.style_none,
                  color="rgba(0,0,0,0)", textcolor=COL_LABEL, size="tiny")
        label.new(x=s2[0], y=s2[1], text="S2", style=label.style_none,
                  color="rgba(0,0,0,0)", textcolor=COL_LABEL, size="tiny")
        line.new(x1=s1[0], y1=s1[1], x2=head[0], y2=head[1], color=col, width=1, style="dashed")
        line.new(x1=head[0], y1=head[1], x2=s2[0], y2=s2[1], color=col, width=1, style="dashed")
        if len(neck_pts) >= 2:
            nx1, ny1 = neck_pts[0]
            nx2, ny2 = neck_pts[1]
            ext_bar = min(s2[0] + 10, n - 1)
            if nx1 != nx2:
                slope = (ny2 - ny1) / (nx2 - nx1)
                ext_y = ny1 + slope * (ext_bar - nx1)
            else:
                ext_y = ny1
            line.new(x1=nx1, y1=ny1, x2=ext_bar, y2=float(ext_y), color=COL_NECK, width=1, style="dotted")
        else:
            line.new(x1=s1[0], y1=neck_y, x2=min(s2[0] + 10, n - 1), y2=neck_y,
                     color=COL_NECK, width=1, style="dotted")

    elif ptype == "triangle":
        res = det["res_line"]
        sup = det["sup_line"]
        line.new(x1=res[0], y1=res[1], x2=res[2], y2=res[3], color=col, width=1, style="solid")
        line.new(x1=sup[0], y1=sup[1], x2=sup[2], y2=sup[3], color=col, width=1, style="solid")

# --- Plots (minimal) ---
bullish_mask = pattern_score > 0
bearish_mask = pattern_score < 0
plotshape(bullish_mask, title="Bullish Signal", style="triangleup", location="belowbar", color="rgba(0,200,83,0.5)", size="tiny")
plotshape(bearish_mask, title="Bearish Signal", style="triangledown", location="abovebar", color="rgba(255,23,68,0.5)", size="tiny")

plot(pattern_smooth, title="Pattern Score", color="#7C4DFF")
hline(0.0, title="Zero", color="#78909C")
