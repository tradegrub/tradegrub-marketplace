from tg_scripting import *
import numpy as np

indicator("Kagi Chart Overlay", overlay=True)

reversal_mode = input.string("ATR", "Reversal Mode", options=["ATR", "Percent", "Fixed"])
reversal_pct = input.float(4.0, "Reversal %", minval=0.5, maxval=20.0, step=0.5)
reversal_fixed = input.float(1.0, "Reversal Fixed", minval=0.01, step=0.1)
atr_length = input.int(14, "ATR Length", minval=1, maxval=100)
atr_mult = input.float(1.5, "ATR Multiplier", minval=0.1, maxval=5.0, step=0.1)

src = np.array(close, dtype=float)
hi = np.array(high, dtype=float)
lo = np.array(low, dtype=float)
n = len(src)

tr = np.maximum(hi - lo, np.maximum(np.abs(hi - np.roll(src, 1)), np.abs(lo - np.roll(src, 1))))
tr[0] = hi[0] - lo[0]
atr_arr = np.full(n, np.nan)
if n >= atr_length:
    atr_arr[atr_length - 1] = np.mean(tr[:atr_length])
    for i in range(atr_length, n):
        atr_arr[i] = (atr_arr[i - 1] * (atr_length - 1) + tr[i]) / atr_length

rev_amount = np.full(n, np.nan)
for i in range(n):
    if reversal_mode == "ATR":
        rev_amount[i] = atr_arr[i] * atr_mult if not np.isnan(atr_arr[i]) else src[i] * reversal_pct / 100.0
    elif reversal_mode == "Percent":
        rev_amount[i] = src[i] * reversal_pct / 100.0
    else:
        rev_amount[i] = reversal_fixed

kagi_line = np.full(n, np.nan)
is_yang = np.ones(n, dtype=bool)

if n >= 2:
    direction = 1 if src[1] >= src[0] else -1
    kagi_line[0] = src[0]
    last_peak = src[0]
    last_trough = src[0]
    yang = True
    current_level = src[0]

    for i in range(1, n):
        price = src[i]
        rev = rev_amount[i] if not np.isnan(rev_amount[i]) else rev_amount[i - 1]

        if direction == 1:
            if price >= current_level:
                current_level = price
                if current_level > last_peak:
                    last_peak = current_level
                    yang = True
            elif current_level - price >= rev:
                last_peak = current_level
                direction = -1
                current_level = price
                if current_level < last_trough:
                    last_trough = current_level
                    yang = False
        else:
            if price <= current_level:
                current_level = price
                if current_level < last_trough:
                    last_trough = current_level
                    yang = False
            elif price - current_level >= rev:
                last_trough = current_level
                direction = 1
                current_level = price
                if current_level > last_peak:
                    last_peak = current_level
                    yang = True

        kagi_line[i] = current_level
        is_yang[i] = yang

    yang_line = np.where(is_yang, kagi_line, np.nan)
    yin_line = np.where(~is_yang, kagi_line, np.nan)

    plot(yang_line.tolist(), title="Yang (Bull)", color="#4CAF50", linewidth=3)
    plot(yin_line.tolist(), title="Yin (Bear)", color="#EF5350", linewidth=1)

    transitions_bull = np.zeros(n, dtype=bool)
    transitions_bear = np.zeros(n, dtype=bool)
    for i in range(1, n):
        if is_yang[i] and not is_yang[i - 1]:
            transitions_bull[i] = True
        elif not is_yang[i] and is_yang[i - 1]:
            transitions_bear[i] = True

    plotshape(transitions_bull.tolist(), title="Yang Start", style="triangleup", location="belowbar", color="#4CAF50", size="tiny")
    plotshape(transitions_bear.tolist(), title="Yin Start", style="triangledown", location="abovebar", color="#EF5350", size="tiny")
