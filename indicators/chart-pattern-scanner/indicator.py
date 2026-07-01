from tg_scripting import *

indicator("Chart Pattern Scanner", overlay=True)

# --- Inputs ---
swing_len = input.int(5, "Swing Detection Length", minval=2, maxval=20)
lookback = input.int(100, "Pattern Lookback Bars", minval=30, maxval=300)
tolerance = input.float(0.02, "Pattern Tolerance (%)", minval=0.005, maxval=0.10)
min_swings = input.int(5, "Min Swings for Pattern", minval=3, maxval=10)
show_trendlines = input.bool(True, "Show Trendlines")
show_labels = input.bool(True, "Show Labels")
show_levels = input.bool(True, "Show Levels")

# --- Swing High/Low Detection using numpy turning points ---
n = len(close)

# Compute first differences and their signs
high_diff = np.diff(high)
low_diff = np.diff(low)
high_sign = np.sign(high_diff)
low_sign = np.sign(low_diff)

# Detect sign changes (turning points)
high_sign_change = np.diff(high_sign)
low_sign_change = np.diff(low_sign)

# Swing highs: sign goes from +1 to -1 (value = -2)
# Swing lows: sign goes from -1 to +1 (value = +2)
swing_high_raw = np.pad(high_sign_change == -2, (2, 0), constant_values=False)
swing_low_raw = np.pad(low_sign_change == 2, (2, 0), constant_values=False)

# Confirm swings with neighborhood check (must be highest/lowest in window)
swing_high_mask = np.zeros(n, dtype=bool)
swing_low_mask = np.zeros(n, dtype=bool)

for i in range(swing_len, n - swing_len):
    window_start = max(0, i - swing_len)
    window_end = min(n, i + swing_len + 1)
    if swing_high_raw[i] and high[i] == np.max(high[window_start:window_end]):
        swing_high_mask[i] = True
    if swing_low_raw[i] and low[i] == np.min(low[window_start:window_end]):
        swing_low_mask[i] = True

# Extract swing indices and values
sh_indices = np.where(swing_high_mask)[0]
sl_indices = np.where(swing_low_mask)[0]
sh_values = high[sh_indices]
sl_values = low[sl_indices]

# --- Pattern Detection Functions ---
pattern_score = np.zeros(n)
pattern_label = np.full(n, 0)  # 0=none, 1=double_top, 2=double_bot, 3=h&s, 4=asc_tri, 5=desc_tri, 6=wedge

def check_double_top(sh_idx, sh_val, tol):
    """Detect double top: two swing highs at similar levels with a valley between."""
    signals = np.zeros(n)
    for i in range(len(sh_idx) - 1):
        price_diff = np.abs(sh_val[i] - sh_val[i + 1]) / sh_val[i]
        if price_diff < tol:
            bar_gap = sh_idx[i + 1] - sh_idx[i]
            if 5 < bar_gap < lookback:
                # Find the low between the two peaks
                between_low = np.min(low[sh_idx[i]:sh_idx[i + 1] + 1])
                neckline_dist = (sh_val[i] - between_low) / sh_val[i]
                if neckline_dist > tol:
                    signals[sh_idx[i + 1]] = -neckline_dist * 100
    return signals

def check_double_bottom(sl_idx, sl_val, tol):
    """Detect double bottom: two swing lows at similar levels with a peak between."""
    signals = np.zeros(n)
    for i in range(len(sl_idx) - 1):
        price_diff = np.abs(sl_val[i] - sl_val[i + 1]) / sl_val[i]
        if price_diff < tol:
            bar_gap = sl_idx[i + 1] - sl_idx[i]
            if 5 < bar_gap < lookback:
                between_high = np.max(high[sl_idx[i]:sl_idx[i + 1] + 1])
                neckline_dist = (between_high - sl_val[i]) / sl_val[i]
                if neckline_dist > tol:
                    signals[sl_idx[i + 1]] = neckline_dist * 100
    return signals

def check_head_and_shoulders(sh_idx, sh_val, sl_idx, sl_val, tol):
    """Detect head and shoulders: three peaks, middle highest, shoulders similar."""
    signals = np.zeros(n)
    for i in range(len(sh_idx) - 2):
        left_s, head, right_s = sh_val[i], sh_val[i + 1], sh_val[i + 2]
        # Head must be highest
        if head > left_s and head > right_s:
            # Shoulders within tolerance of each other
            shoulder_diff = np.abs(left_s - right_s) / left_s
            if shoulder_diff < tol * 2:
                # Head meaningfully higher than shoulders
                head_prominence = (head - (left_s + right_s) / 2) / head
                if head_prominence > tol:
                    bar_span = sh_idx[i + 2] - sh_idx[i]
                    if bar_span < lookback:
                        signals[sh_idx[i + 2]] = -head_prominence * 100
    return signals

def detect_triangle(sh_idx, sh_val, sl_idx, sl_val, tol):
    """Detect ascending/descending triangles and wedges via trendline slopes."""
    signals = np.zeros(n)
    triangle_type = np.zeros(n)  # 4=ascending, 5=descending, 6=wedge

    if len(sh_idx) < 3 or len(sl_idx) < 3:
        return signals, triangle_type

    # Use recent swings for trendline fitting
    recent_sh = sh_idx[-min(5, len(sh_idx)):]
    recent_sl = sl_idx[-min(5, len(sl_idx)):]
    recent_sh_vals = sh_val[-min(5, len(sh_val)):]
    recent_sl_vals = sl_val[-min(5, len(sl_val)):]

    if len(recent_sh) >= 2 and len(recent_sl) >= 2:
        # Linear regression on swing highs and lows
        sh_slope, sh_intercept = np.polyfit(recent_sh.astype(float), recent_sh_vals, 1)
        sl_slope, sl_intercept = np.polyfit(recent_sl.astype(float), recent_sl_vals, 1)

        # Normalize slopes by price level
        avg_price = np.mean(close[-lookback:]) if n > lookback else np.mean(close)
        sh_slope_norm = sh_slope / avg_price
        sl_slope_norm = sl_slope / avg_price

        signal_bar = max(recent_sh[-1], recent_sl[-1])

        # Ascending triangle: flat top, rising bottom
        if np.abs(sh_slope_norm) < tol * 0.5 and sl_slope_norm > tol * 0.5:
            signals[signal_bar] = 50.0
            triangle_type[signal_bar] = 4

        # Descending triangle: flat bottom, falling top
        elif np.abs(sl_slope_norm) < tol * 0.5 and sh_slope_norm < -tol * 0.5:
            signals[signal_bar] = -50.0
            triangle_type[signal_bar] = 5

        # Wedge: both converging
        elif sh_slope_norm < -tol * 0.3 and sl_slope_norm > tol * 0.3:
            # Falling wedge (bullish)
            if sh_slope_norm < 0 and sl_slope_norm < 0:
                signals[signal_bar] = 40.0
                triangle_type[signal_bar] = 6
            # Rising wedge (bearish)
            elif sh_slope_norm > 0 and sl_slope_norm > 0:
                signals[signal_bar] = -40.0
                triangle_type[signal_bar] = 6
            else:
                # Symmetric converging
                signals[signal_bar] = 30.0
                triangle_type[signal_bar] = 6

    return signals, triangle_type

# --- Run all pattern detectors ---
dt_signals = check_double_top(sh_indices, sh_values, tolerance)
db_signals = check_double_bottom(sl_indices, sl_values, tolerance)
hs_signals = check_head_and_shoulders(sh_indices, sh_values, sl_indices, sl_values, tolerance)
tri_signals, tri_types = detect_triangle(sh_indices, sh_values, sl_indices, sl_values, tolerance)

# Composite pattern score
pattern_score = dt_signals + db_signals + hs_signals + tri_signals
pattern_smooth = ta.sma(pattern_score, 3)

# Determine active pattern type at each bar
pattern_label = np.where(dt_signals != 0, 1,
                np.where(db_signals != 0, 2,
                np.where(hs_signals != 0, 3,
                np.where(tri_types != 0, tri_types, 0))))

# --- Trendline projection using polyfit on recent swing highs/lows ---
resistance_line = np.full(n, np.nan)
support_line = np.full(n, np.nan)

if show_trendlines and len(sh_indices) >= 2 and len(sl_indices) >= 2:
    sh_coeff = np.polyfit(sh_indices[-3:].astype(float), sh_values[-3:], 1) if len(sh_indices) >= 3 else np.polyfit(sh_indices[-2:].astype(float), sh_values[-2:], 1)
    sl_coeff = np.polyfit(sl_indices[-3:].astype(float), sl_values[-3:], 1) if len(sl_indices) >= 3 else np.polyfit(sl_indices[-2:].astype(float), sl_values[-2:], 1)

    start_bar = min(sh_indices[-3] if len(sh_indices) >= 3 else sh_indices[-2],
                    sl_indices[-3] if len(sl_indices) >= 3 else sl_indices[-2])
    for b in range(start_bar, n):
        resistance_line[b] = np.polyval(sh_coeff, float(b))
        support_line[b] = np.polyval(sl_coeff, float(b))

# --- Plots ---
plotshape(swing_high_mask, title="Swing High", style="triangledown", location="abovebar", color="#EF5350")
plotshape(swing_low_mask, title="Swing Low", style="triangleup", location="belowbar", color="#26A69A")

plot(resistance_line, title="Resistance Trendline", color="#EF5350")
plot(support_line, title="Support Trendline", color="#26A69A")

# Pattern signals
bullish_pattern = pattern_score > 0
bearish_pattern = pattern_score < 0
plotshape(bullish_pattern, title="Bullish Pattern", style="diamond", location="belowbar", color="#00C853")
plotshape(bearish_pattern, title="Bearish Pattern", style="diamond", location="abovebar", color="#FF1744")

plot(pattern_smooth, title="Pattern Score", color="#7C4DFF")
hline(0.0, title="Zero Line", color="#78909C")

bgcolor(np.abs(pattern_score) > 30, color=np.where(pattern_score > 30, "rgba(0,200,83,0.1)", "rgba(255,23,68,0.1)"))

# --- Rich annotations ---
pattern_names = {1: "Double Top", 2: "Double Bottom", 3: "Head & Shoulders",
                 4: "Asc Triangle", 5: "Desc Triangle", 6: "Wedge"}
pattern_colors = {1: "#ef5350", 2: "#00e676", 3: "#ef5350",
                  4: "#00e676", 5: "#ef5350", 6: "#42a5f5"}
pattern_styles = {1: label.style_label_down, 2: label.style_label_up, 3: label.style_label_down,
                  4: label.style_label_up, 5: label.style_label_down, 6: label.style_label_down}

last_pattern_idx = -100
cooldown = 20

for i in range(swing_len, n):
    p_type = int(pattern_label[i])
    if p_type == 0:
        continue
    if (i - last_pattern_idx) < cooldown:
        continue
    last_pattern_idx = i

    if show_labels:
        p_name = pattern_names.get(p_type, "Pattern")
        p_color = pattern_colors.get(p_type, "#888888")
        p_style = pattern_styles.get(p_type, label.style_label_down)
        y_pos = float(high[i]) if pattern_score[i] < 0 else float(low[i])
        label.new(
            x=i, y=y_pos,
            text=p_name,
            style=p_style,
            color="rgba(0,0,0,0)",
            textcolor=p_color,
            size="normal"
        )

    if show_levels and show_trendlines and not np.isnan(resistance_line[i]) and not np.isnan(support_line[i]):
        label.new(
            x=i, y=float(resistance_line[i]),
            text="Resistance",
            style=label.style_none,
            color="rgba(0,0,0,0)",
            textcolor="#ef5350",
            size="tiny"
        )
        label.new(
            x=i, y=float(support_line[i]),
            text="Support",
            style=label.style_none,
            color="rgba(0,0,0,0)",
            textcolor="#26A69A",
            size="tiny"
        )
