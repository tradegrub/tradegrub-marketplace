from tg_scripting import *
import numpy as np

indicator("Fair Value Gap Detector", overlay=True)

min_gap_atr = input.float(0.5, "Min Gap Size (ATR)", minval=0.1, maxval=3.0, step=0.1)
max_gaps = input.int(10, "Max Displayed Gaps", minval=1, maxval=30)
show_bull = input.bool(True, "Show Bullish FVG")
show_bear = input.bool(True, "Show Bearish FVG")
show_labels = input.bool(True, "Show Labels")

n = len(close)
atr = ta.atr(high, low, close, 14)

bull_fvg = np.full(n, False)
bear_fvg = np.full(n, False)

bull_gaps = []
bear_gaps = []

for i in range(2, n):
    if atr[i] <= 0:
        continue

    # Bullish FVG: candle 3 low > candle 1 high (gap up)
    gap_up = low[i] - high[i - 2]
    if gap_up > min_gap_atr * atr[i]:
        bull_fvg[i] = True
        bull_gaps.append((i - 1, float(high[i - 2]), float(low[i])))

    # Bearish FVG: candle 1 low > candle 3 high (gap down)
    gap_down = low[i - 2] - high[i]
    if gap_down > min_gap_atr * atr[i]:
        bear_fvg[i] = True
        bear_gaps.append((i - 1, float(high[i]), float(low[i - 2])))

# Draw recent gaps
bull_gaps = bull_gaps[-max_gaps:]
bear_gaps = bear_gaps[-max_gaps:]

if show_bull:
    for mid_bar, bottom, top in bull_gaps:
        box.new(left=mid_bar - 1, top=top, right=min(mid_bar + 8, n - 1), bottom=bottom,
                border_color="rgba(0,230,118,0.3)", bgcolor="rgba(0,230,118,0.05)")
    if show_labels:
        for mid_bar, bottom, top in bull_gaps[-5:]:
            label.new(x=mid_bar, y=bottom, text="FVG",
                      style=label.style_label_up, color="rgba(0,230,118,0.25)",
                      textcolor="#00e676", size="tiny")

if show_bear:
    for mid_bar, bottom, top in bear_gaps:
        box.new(left=mid_bar - 1, top=top, right=min(mid_bar + 8, n - 1), bottom=bottom,
                border_color="rgba(255,23,68,0.3)", bgcolor="rgba(255,23,68,0.05)")
    if show_labels:
        for mid_bar, bottom, top in bear_gaps[-5:]:
            label.new(x=mid_bar, y=top, text="FVG",
                      style=label.style_label_down, color="rgba(255,23,68,0.25)",
                      textcolor="#ff1744", size="tiny")

plotshape(bull_fvg, title="Bull FVG", shape="triangleup", location="belowbar", color="#00e676", size="small")
plotshape(bear_fvg, title="Bear FVG", shape="triangledown", location="abovebar", color="#ff1744", size="small")

fvg_signal = np.where(bull_fvg, 1, np.where(bear_fvg, -1, 0))
plot(fvg_signal, title="FVG Signal", display="none")
