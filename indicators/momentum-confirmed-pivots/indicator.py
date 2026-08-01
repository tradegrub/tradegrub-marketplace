from tg_scripting import *
import numpy as np

indicator("Momentum Confirmed Pivots", overlay=True)

pivot_len = input.int(10, "Pivot Lookback", minval=3, maxval=50)
rsi_len = input.int(14, "RSI Length", minval=2, maxval=50)
rsi_confirm = input.float(50.0, "RSI Confirmation Level", minval=20.0, maxval=80.0, step=5.0)
show_levels = input.bool(True, "Extend Pivot Levels")

cl = np.array(close, dtype=np.float64)
hi = np.array(high, dtype=np.float64)
lo = np.array(low, dtype=np.float64)
n = len(cl)

rsi_vals = np.array(ta.rsi(close, rsi_len), dtype=np.float64)

pivot_highs = np.full(n, np.nan)
pivot_lows = np.full(n, np.nan)

for i in range(pivot_len, n - pivot_len):
    window_hi = hi[i - pivot_len:i + pivot_len + 1]
    if hi[i] == np.max(window_hi):
        pivot_highs[i] = hi[i]
    window_lo = lo[i - pivot_len:i + pivot_len + 1]
    if lo[i] == np.min(window_lo):
        pivot_lows[i] = lo[i]

confirmed_high = np.full(n, np.nan)
confirmed_low = np.full(n, np.nan)

for i in range(pivot_len, n):
    ph_idx = i - pivot_len
    if not np.isnan(pivot_highs[ph_idx]):
        if not np.isnan(rsi_vals[ph_idx]) and rsi_vals[ph_idx] > rsi_confirm:
            confirmed_high[ph_idx] = pivot_highs[ph_idx]
            label.new(
                x=ph_idx, y=float(hi[ph_idx]),
                text="PH",
                style=label.style_label_down,
                color="rgba(239,83,80,0.4)",
                textcolor="#ef5350",
                size="tiny"
            )
            if show_levels:
                end_x = min(ph_idx + 30, n - 1)
                line.new(
                    x1=ph_idx, y1=float(hi[ph_idx]),
                    x2=end_x, y2=float(hi[ph_idx]),
                    color="rgba(239,83,80,0.3)", width=1, style=line.style_dotted
                )

    if not np.isnan(pivot_lows[ph_idx]):
        if not np.isnan(rsi_vals[ph_idx]) and rsi_vals[ph_idx] < (100 - rsi_confirm):
            confirmed_low[ph_idx] = pivot_lows[ph_idx]
            label.new(
                x=ph_idx, y=float(lo[ph_idx]),
                text="PL",
                style=label.style_label_up,
                color="rgba(38,166,154,0.4)",
                textcolor="#26a69a",
                size="tiny"
            )
            if show_levels:
                end_x = min(ph_idx + 30, n - 1)
                line.new(
                    x1=ph_idx, y1=float(lo[ph_idx]),
                    x2=end_x, y2=float(lo[ph_idx]),
                    color="rgba(38,166,154,0.3)", width=1, style=line.style_dotted
                )
