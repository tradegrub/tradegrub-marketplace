from tg_scripting import *
import numpy as np

indicator("Order Block Scanner", overlay=True)

lookback = input.int(10, "Lookback", minval=3, maxval=50)
min_impulse = input.float(1.5, "Min Impulse (ATR mult)", minval=0.5, maxval=5.0, step=0.1)
max_blocks = input.int(5, "Max Active Blocks", minval=1, maxval=20)
show_labels = input.bool(True, "Show Labels")

n = len(close)
atr = ta.atr(high, low, close, 14)

body = np.abs(close - open)
bull_candle = close > open
bear_candle = close < open

# Detect impulse candles followed by strong continuation
bull_ob = np.full(n, False)
bear_ob = np.full(n, False)

for i in range(2, n):
    impulse_size = abs(close[i] - open[i])
    if atr[i] <= 0:
        continue

    # Bullish OB: bearish candle before a strong bullish impulse
    if bull_candle[i] and impulse_size > min_impulse * atr[i]:
        if bear_candle[i - 1]:
            bull_ob[i - 1] = True

    # Bearish OB: bullish candle before a strong bearish impulse
    if bear_candle[i] and impulse_size > min_impulse * atr[i]:
        if bull_candle[i - 1]:
            bear_ob[i - 1] = True

# Draw boxes for order blocks
bull_blocks = []
bear_blocks = []

for i in range(n):
    if bull_ob[i] and len(bull_blocks) < max_blocks:
        bull_blocks.append((i, float(low[i]), float(high[i])))
    if bear_ob[i] and len(bear_blocks) < max_blocks:
        bear_blocks.append((i, float(low[i]), float(high[i])))

# Keep only recent blocks
bull_blocks = bull_blocks[-max_blocks:]
bear_blocks = bear_blocks[-max_blocks:]

for start, bottom, top in bull_blocks:
    end = min(start + lookback, n - 1)
    box.new(left=start, top=top, right=end, bottom=bottom,
            border_color="rgba(0,230,118,0.4)", bgcolor="rgba(0,230,118,0.06)")
    if show_labels:
        label.new(x=start, y=bottom, text="Bull OB",
                  style=label.style_label_up, color="rgba(0,230,118,0.3)",
                  textcolor="#00e676", size="small")

for start, bottom, top in bear_blocks:
    end = min(start + lookback, n - 1)
    box.new(left=start, top=top, right=end, bottom=bottom,
            border_color="rgba(255,23,68,0.4)", bgcolor="rgba(255,23,68,0.06)")
    if show_labels:
        label.new(x=start, y=top, text="Bear OB",
                  style=label.style_label_down, color="rgba(255,23,68,0.3)",
                  textcolor="#ff1744", size="small")

plotshape(bull_ob, title="Bull OB", shape="triangleup", location="belowbar", color="#00e676", size="small")
plotshape(bear_ob, title="Bear OB", shape="triangledown", location="abovebar", color="#ff1744", size="small")

ob_signal = np.where(bull_ob, 1, np.where(bear_ob, -1, 0))
plot(ob_signal, title="OB Signal", display="none")
