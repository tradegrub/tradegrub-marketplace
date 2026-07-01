from tg_scripting import *
import numpy as np

indicator("Break of Structure Detector", overlay=True)

swing_len = input.int(5, "Swing Lookback", minval=2, maxval=20)
show_bos = input.bool(True, "Show BOS")
show_choch = input.bool(True, "Show CHoCH")
show_lines = input.bool(True, "Show Structure Lines")

n = len(close)
swing_highs = np.full(n, np.nan)
swing_lows = np.full(n, np.nan)

# Detect swing highs and lows
for i in range(swing_len, n - swing_len):
    is_sh = True
    is_sl = True
    for j in range(1, swing_len + 1):
        if high[i] <= high[i - j] or high[i] <= high[i + j]:
            is_sh = False
        if low[i] >= low[i - j] or low[i] >= low[i + j]:
            is_sl = False
    if is_sh:
        swing_highs[i] = high[i]
    if is_sl:
        swing_lows[i] = low[i]

# Track structure breaks
bos_bull = np.full(n, False)
bos_bear = np.full(n, False)
choch_bull = np.full(n, False)
choch_bear = np.full(n, False)

last_sh = np.nan
last_sl = np.nan
prev_sh = np.nan
prev_sl = np.nan
trend = 0  # 1=bullish, -1=bearish

cooldown = swing_len * 2
last_signal_bar = -100

for i in range(swing_len, n):
    if not np.isnan(swing_highs[i]):
        prev_sh = last_sh
        last_sh = swing_highs[i]
    if not np.isnan(swing_lows[i]):
        prev_sl = last_sl
        last_sl = swing_lows[i]

    if np.isnan(last_sh) or np.isnan(last_sl):
        continue
    if (i - last_signal_bar) < cooldown:
        continue

    # BOS: continuation break
    if close[i] > last_sh and trend >= 0:
        bos_bull[i] = True
        trend = 1
        last_signal_bar = i
    elif close[i] < last_sl and trend <= 0:
        bos_bear[i] = True
        trend = -1
        last_signal_bar = i
    # CHoCH: reversal break
    elif close[i] > last_sh and trend == -1:
        choch_bull[i] = True
        trend = 1
        last_signal_bar = i
    elif close[i] < last_sl and trend == 1:
        choch_bear[i] = True
        trend = -1
        last_signal_bar = i

if show_bos:
    plotshape(bos_bull, title="BOS Bull", shape="triangleup", location="belowbar", color="#00e676", size="small")
    plotshape(bos_bear, title="BOS Bear", shape="triangledown", location="abovebar", color="#ff1744", size="small")

if show_choch:
    plotshape(choch_bull, title="CHoCH Bull", shape="triangleup", location="belowbar", color="#42A5F5", size="small")
    plotshape(choch_bear, title="CHoCH Bear", shape="triangledown", location="abovebar", color="#ff9800", size="small")

# Labels for CHoCH (rarer, more important)
for i in range(n):
    if choch_bull[i]:
        label.new(x=i, y=float(low[i]), text="CHoCH", style=label.style_label_up,
                  color="rgba(66,165,245,0.3)", textcolor="#42A5F5", size="small")
    if choch_bear[i]:
        label.new(x=i, y=float(high[i]), text="CHoCH", style=label.style_label_down,
                  color="rgba(255,152,0,0.3)", textcolor="#ff9800", size="small")

# Structure level lines
if show_lines:
    sh_line = np.where(~np.isnan(swing_highs), swing_highs, np.nan)
    sl_line = np.where(~np.isnan(swing_lows), swing_lows, np.nan)
    # Forward fill
    for i in range(1, n):
        if np.isnan(sh_line[i]) and not np.isnan(sh_line[i - 1]):
            sh_line[i] = sh_line[i - 1]
        if np.isnan(sl_line[i]) and not np.isnan(sl_line[i - 1]):
            sl_line[i] = sl_line[i - 1]
    plot(sh_line, title="Swing Highs", color="rgba(255,23,68,0.4)", linewidth=1, style="stepline")
    plot(sl_line, title="Swing Lows", color="rgba(0,230,118,0.4)", linewidth=1, style="stepline")
