from tg_scripting import *
import numpy as np

indicator("Harmonic Pattern Scanner", overlay=True)

zz_len = input.int(10, "Zigzag Length", minval=3, maxval=50)
tolerance = input.float(0.10, "Ratio Tolerance", minval=0.01, maxval=0.30)
min_legs = input.int(5, "Min Bars Per Leg", minval=2, maxval=30)

src = np.array(close, dtype=float)
hi = np.array(high, dtype=float)
lo = np.array(low, dtype=float)
n = len(src)

# --- Zigzag swing detection ---
swings = []  # list of (index, price, type) where type is 1=high, -1=low

direction = 0
last_hi_idx = 0
last_lo_idx = 0
last_hi_val = hi[0]
last_lo_val = lo[0]

for i in range(1, n):
    is_swing_hi = True
    is_swing_lo = True
    for j in range(max(0, i - zz_len), min(n, i + zz_len + 1)):
        if j == i:
            continue
        if hi[j] > hi[i]:
            is_swing_hi = False
        if lo[j] < lo[i]:
            is_swing_lo = False
        if not is_swing_hi and not is_swing_lo:
            break

    if is_swing_hi and direction != 1:
        if direction == -1 and swings:
            swings.append((last_lo_idx, last_lo_val, -1))
        direction = 1
        last_hi_idx = i
        last_hi_val = hi[i]
    elif is_swing_hi and direction == 1:
        if hi[i] > last_hi_val:
            last_hi_idx = i
            last_hi_val = hi[i]

    if is_swing_lo and direction != -1:
        if direction == 1 and swings:
            swings.append((last_hi_idx, last_hi_val, 1))
        direction = -1
        last_lo_idx = i
        last_lo_val = lo[i]
    elif is_swing_lo and direction == -1:
        if lo[i] < last_lo_val:
            last_lo_idx = i
            last_lo_val = lo[i]

if direction == 1:
    swings.append((last_hi_idx, last_hi_val, 1))
elif direction == -1:
    swings.append((last_lo_idx, last_lo_val, -1))

# --- Fibonacci ratio check ---
def ratio_match(actual, target, tol):
    return abs(actual - target) <= target * tol

# Pattern definitions: (name, B_ratio_of_XA, D_ratio_of_XA, color)
patterns = [
    ("Gartley", 0.618, 0.786, "#4CAF50"),
    ("Butterfly", 0.786, 1.27, "#2196F3"),
    ("Bat", 0.441, 0.886, "#FF9800"),
    ("Crab", 0.500, 1.618, "#E91E63"),
]

# Bat has B range 0.382-0.5, use midpoint for matching
bat_b_low = 0.382
bat_b_high = 0.500
crab_b_low = 0.382
crab_b_high = 0.618

labels_x = []
labels_y = []
labels_text = []
lines_data = []

# Scan for XABCD patterns in the swing list
for i in range(len(swings) - 4):
    X_idx, X_price, X_type = swings[i]
    A_idx, A_price, A_type = swings[i + 1]
    B_idx, B_price, B_type = swings[i + 2]
    C_idx, C_price, C_type = swings[i + 3]
    D_idx, D_price, D_type = swings[i + 4]

    # Ensure alternating swing types
    if X_type == A_type or A_type == B_type or B_type == C_type or C_type == D_type:
        continue

    # Ensure minimum bars between legs
    if (A_idx - X_idx < min_legs or B_idx - A_idx < min_legs or
            C_idx - B_idx < min_legs or D_idx - C_idx < min_legs):
        continue

    xa = abs(A_price - X_price)
    if xa == 0:
        continue

    ab = abs(B_price - A_price)
    bc = abs(C_price - B_price)
    cd = abs(D_price - C_price)

    b_ratio = ab / xa  # B retracement of XA
    d_retrace = abs(D_price - A_price) / xa  # D relative to XA from A

    # Check which pattern matches
    matched = None
    matched_color = None

    for pname, b_target, d_target, pcolor in patterns:
        if pname == "Bat":
            b_ok = (bat_b_low * (1 - tolerance) <= b_ratio <= bat_b_high * (1 + tolerance))
        elif pname == "Crab":
            b_ok = (crab_b_low * (1 - tolerance) <= b_ratio <= crab_b_high * (1 + tolerance))
        else:
            b_ok = ratio_match(b_ratio, b_target, tolerance)

        # D ratio: distance from X to D vs XA
        xd = abs(D_price - X_price)
        d_ratio = xd / xa
        d_ok = ratio_match(d_ratio, d_target, tolerance)

        if b_ok and d_ok:
            matched = pname
            matched_color = pcolor
            break

    if matched:
        # Draw pattern lines X-A-B-C-D
        bar_offset_x = n - 1 - X_idx
        bar_offset_a = n - 1 - A_idx
        bar_offset_b = n - 1 - B_idx
        bar_offset_c = n - 1 - C_idx
        bar_offset_d = n - 1 - D_idx

        line.new(bar_offset_x, X_price, bar_offset_a, A_price, matched_color)
        line.new(bar_offset_a, A_price, bar_offset_b, B_price, matched_color)
        line.new(bar_offset_b, B_price, bar_offset_c, C_price, matched_color)
        line.new(bar_offset_c, C_price, bar_offset_d, D_price, matched_color)

        # Label at D point
        label.new(bar_offset_d, D_price, matched)

        # Label each point
        label.new(bar_offset_x, X_price, "X")
        label.new(bar_offset_a, A_price, "A")
        label.new(bar_offset_b, B_price, "B")
        label.new(bar_offset_c, C_price, "C")
        label.new(bar_offset_d, D_price, "D")
