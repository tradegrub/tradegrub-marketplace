from tg_scripting import *
import numpy as np

indicator("Inside Bar Failure", overlay=True)

max_lookforward = input.int(5, "Max Bars After Breakout", minval=2, maxval=20)
show_inside_bars = input.bool(True, "Highlight Inside Bars")
show_range = input.bool(True, "Show Mother Bar Range")
bull_fail_color = "#ff1744"
bear_fail_color = "#00e676"
inside_bg_color = "rgba(255,235,59,0.08)"

n = len(close)

# Detect inside bars: high[i] <= high[i-1] AND low[i] >= low[i-1]
prev_high = np.roll(high, 1)
prev_low = np.roll(low, 1)
prev_high[0] = np.nan
prev_low[0] = np.nan

is_inside_bar = (high <= prev_high) & (low >= prev_low)

# Highlight inside bars with bgcolor
if show_inside_bars:
    plotshape(is_inside_bar.tolist(), title="Inside Bar", style="circle", location="abovebar",
              color="rgba(255,235,59,0.5)", size="tiny")
    bgcolor(is_inside_bar, color=inside_bg_color)

# Track mother bar range and detect breakout failures
for i in range(2, n):
    if not is_inside_bar[i - 1] and not is_inside_bar[i]:
        continue

    # Find the inside bar and its mother bar
    if not is_inside_bar[i]:
        continue

    # Mother bar is i-1
    mother_high = float(high[i - 1])
    mother_low = float(low[i - 1])

    # Draw mother bar range
    if show_range:
        end_x = min(i + max_lookforward, n - 1)
        line.new(
            x1=i - 1, y1=mother_high,
            x2=end_x, y2=mother_high,
            color="rgba(158,158,158,0.4)", width=1, style=line.style_dotted
        )
        line.new(
            x1=i - 1, y1=mother_low,
            x2=end_x, y2=mother_low,
            color="rgba(158,158,158,0.4)", width=1, style=line.style_dotted
        )

    # Monitor subsequent bars for breakout then failure
    bullish_breakout = False
    bearish_breakout = False

    for j in range(i + 1, min(i + 1 + max_lookforward, n)):
        c = float(close[j])

        if not bullish_breakout and not bearish_breakout:
            # Check for initial breakout
            if c > mother_high:
                bullish_breakout = True
            elif c < mother_low:
                bearish_breakout = True
        else:
            # Check for failure (reversal through opposite side)
            if bullish_breakout and c < mother_low:
                label.new(
                    x=j, y=float(high[j]),
                    text="Bull Fail",
                    style=label.style_label_down,
                    color="rgba(255,23,68,0.3)",
                    textcolor=bull_fail_color,
                    size="tiny"
                )
                break
            elif bearish_breakout and c > mother_high:
                label.new(
                    x=j, y=float(low[j]),
                    text="Bear Fail",
                    style=label.style_label_up,
                    color="rgba(0,230,118,0.3)",
                    textcolor=bear_fail_color,
                    size="tiny"
                )
                break
