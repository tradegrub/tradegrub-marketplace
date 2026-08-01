from tg_scripting import *
import numpy as np

indicator("Auto Anchor VWAP", overlay=True)

swing_len = input.int(10, "Swing Length", minval=3, maxval=50)
show_standard = input.bool(True, "Show Standard VWAP")
show_anchors = input.bool(True, "Show Anchored VWAPs")

hi = np.array(high, dtype=float)
lo = np.array(low, dtype=float)
cl = np.array(close, dtype=float)
vol = np.array(volume, dtype=float)
n = len(cl)

typical = (hi + lo + cl) / 3.0
vol_tp = vol * typical

# --- Standard VWAP ---
cum_vol = np.cumsum(vol)
cum_vol_tp = np.cumsum(vol_tp)
cum_vol[cum_vol == 0] = np.nan
standard_vwap = cum_vol_tp / cum_vol

if show_standard:
    plot(standard_vwap.tolist(), title="VWAP", color="#2196F3", linewidth=2)

# --- Find most recent swing high and swing low ---
swing_high_idx = -1
swing_low_idx = -1

for i in range(n - 1 - swing_len, swing_len - 1, -1):
    if swing_high_idx < 0:
        is_swing_high = True
        for j in range(1, swing_len + 1):
            if hi[i - j] >= hi[i] or hi[i + j] >= hi[i]:
                is_swing_high = False
                break
        if is_swing_high:
            swing_high_idx = i

    if swing_low_idx < 0:
        is_swing_low = True
        for j in range(1, swing_len + 1):
            if lo[i - j] <= lo[i] or lo[i + j] <= lo[i]:
                is_swing_low = False
                break
        if is_swing_low:
            swing_low_idx = i

    if swing_high_idx >= 0 and swing_low_idx >= 0:
        break

# --- Anchored VWAPs ---
if show_anchors:
    if swing_high_idx >= 0:
        anchor_vol = np.cumsum(vol[swing_high_idx:])
        anchor_vol_tp = np.cumsum(vol_tp[swing_high_idx:])
        anchor_vol[anchor_vol == 0] = np.nan
        vwap_from_high = np.full(n, np.nan)
        vwap_from_high[swing_high_idx:] = anchor_vol_tp / anchor_vol
        plot(vwap_from_high.tolist(), title="VWAP from High", color="#f44336", linewidth=2)
        label.new(x=swing_high_idx, y=float(hi[swing_high_idx]),
                  text="SH", color="#f44336", textcolor="#ffffff",
                  style="label_down", size="tiny")

    if swing_low_idx >= 0:
        anchor_vol = np.cumsum(vol[swing_low_idx:])
        anchor_vol_tp = np.cumsum(vol_tp[swing_low_idx:])
        anchor_vol[anchor_vol == 0] = np.nan
        vwap_from_low = np.full(n, np.nan)
        vwap_from_low[swing_low_idx:] = anchor_vol_tp / anchor_vol
        plot(vwap_from_low.tolist(), title="VWAP from Low", color="#4CAF50", linewidth=2)
        label.new(x=swing_low_idx, y=float(lo[swing_low_idx]),
                  text="SL", color="#4CAF50", textcolor="#ffffff",
                  style="label_up", size="tiny")
