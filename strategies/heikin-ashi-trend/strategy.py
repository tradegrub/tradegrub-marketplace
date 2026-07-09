# Heikin-Ashi Trend Following Strategy
from tg_scripting import *

indicator("Heikin Ashi Trend", overlay=True)

ema_fast = input.int(8, "Fast EMA Length", minval=3, maxval=20)
ema_slow = input.int(21, "Slow EMA Length", minval=10, maxval=50)
atr_len = input.int(14, "ATR Length", minval=5, maxval=50)
atr_trail = input.float(2.0, "ATR Trailing Multiplier", minval=1.0, maxval=5.0)
show_labels = input.bool(True, "Show Labels")
show_levels = input.bool(True, "Show Entry/Stop/TP Levels")

# Compute Heikin-Ashi candles using numpy
ha_close = (open + high + low + close) / 4.0

# For ha_open, use rolling calculation: start with (open+close)/2, then average with prior ha_open
ha_open = np.empty_like(close)
ha_open[0] = (open[0] + close[0]) / 2.0
for i in range(1, len(close)):
    ha_open[i] = (ha_open[i - 1] + ha_close[i - 1]) / 2.0

ha_high = np.maximum(high, np.maximum(ha_open, ha_close))
ha_low = np.minimum(low, np.minimum(ha_open, ha_close))

# EMA trend confirmation on HA close
fast_ema = ta.ema(ha_close, ema_fast)
slow_ema = ta.ema(ha_close, ema_slow)
atr = ta.atr(high, low, close, atr_len)

# HA trend signals (array-based)
ha_bullish = ha_close > ha_open
ha_bearish = ha_close < ha_open
prev_ha_bearish = np.roll(ha_bearish, 1)
prev_ha_bullish = np.roll(ha_bullish, 1)
bull_trend = fast_ema > slow_ema
bear_trend = fast_ema < slow_ema

# Entry on HA color flip with EMA confirmation
ha_flip_bull = ha_bullish & prev_ha_bearish & bull_trend
ha_flip_bear = ha_bearish & prev_ha_bullish & bear_trend

n = len(close)
for i in range(1, n):
    strategy.set_bar_index(i)
    if ha_flip_bull[i]:
        strategy.entry("Long", strategy.LONG)

    if ha_flip_bear[i]:
        strategy.entry("Short", strategy.SHORT)

    # Trailing stop exits
    if ha_bearish[i] and not bull_trend[i]:
        strategy.close("Long")
    if ha_bullish[i] and not bear_trend[i]:
        strategy.close("Short")

plotcandle(ha_open, ha_high, ha_low, ha_close, title="Heikin-Ashi")
plot(fast_ema, title="Fast EMA", color="blue")
plot(slow_ema, title="Slow EMA", color="red")
plotshape(ha_flip_bull, title="HA Bull Flip", style="triangleup", location="belowbar", color="green")
plotshape(ha_flip_bear, title="HA Bear Flip", style="triangledown", location="abovebar", color="red")

# --- Rich annotations ---
n = len(close)
ha_bull_arr = ha_close > ha_open
ha_bear_arr = ha_close < ha_open
prev_ha_bear = np.roll(ha_bear_arr, 1)
prev_ha_bull = np.roll(ha_bull_arr, 1)
fast_ema_arr = ta.ema(ha_close, ema_fast)
slow_ema_arr = ta.ema(ha_close, ema_slow)
bull_trend_arr = fast_ema_arr > slow_ema_arr
bear_trend_arr = fast_ema_arr < slow_ema_arr
flip_bull_arr = ha_bull_arr & prev_ha_bear & bull_trend_arr
flip_bear_arr = ha_bear_arr & prev_ha_bull & bear_trend_arr
last_signal_idx = -100

for i in range(1, n):
    if i - last_signal_idx < 15:
        continue

    if flip_bull_arr[i]:
        last_signal_idx = i
        if show_labels:
            label.new(x=i, y=float(low[i]),
                      text="HA Flip\nTrend Up",
                      style=label.style_label_up,
                      color="#00e676", textcolor="#000000", size="normal")
        if show_levels:
            entry_price = float(close[i])
            sl_price = float(close[i] - atr[i] * atr_trail)
            tp_price = float(close[i] + atr[i] * atr_trail * 2)
            end_bar = min(i + 30, n - 1)
            line.new(x1=i, y1=entry_price, x2=end_bar, y2=entry_price,
                     color="#42a5f5", width=1, style=line.style_dashed)
            label.new(x=i + 2, y=entry_price, text="Entry",
                      style=label.style_label_left, color="rgba(66,165,245,0.2)",
                      textcolor="#42a5f5", size="small")
            line.new(x1=i, y1=sl_price, x2=end_bar, y2=sl_price,
                     color="#ef5350", width=1, style=line.style_dashed)
            label.new(x=i + 2, y=sl_price, text="Stop Loss",
                      style=label.style_label_left, color="rgba(239,83,80,0.2)",
                      textcolor="#ef5350", size="small")
            line.new(x1=i, y1=tp_price, x2=end_bar, y2=tp_price,
                     color="#00e676", width=1, style=line.style_dashed)
            label.new(x=i + 2, y=tp_price, text="Take Profit",
                      style=label.style_label_left, color="rgba(0,230,118,0.2)",
                      textcolor="#00e676", size="small")
            box.new(left=i, top=tp_price, right=end_bar, bottom=sl_price,
                    border_color="rgba(66,165,245,0.15)", bgcolor="rgba(66,165,245,0.03)")

    elif flip_bear_arr[i]:
        last_signal_idx = i
        if show_labels:
            label.new(x=i, y=float(high[i]),
                      text="HA Flip\nTrend Down",
                      style=label.style_label_down,
                      color="#ef5350", textcolor="#ffffff", size="normal")
        if show_levels:
            entry_price = float(close[i])
            sl_price = float(close[i] + atr[i] * atr_trail)
            tp_price = float(close[i] - atr[i] * atr_trail * 2)
            end_bar = min(i + 30, n - 1)
            line.new(x1=i, y1=entry_price, x2=end_bar, y2=entry_price,
                     color="#42a5f5", width=1, style=line.style_dashed)
            line.new(x1=i, y1=sl_price, x2=end_bar, y2=sl_price,
                     color="#ef5350", width=1, style=line.style_dashed)
            label.new(x=i + 2, y=sl_price, text="Stop Loss",
                      style=label.style_label_left, color="rgba(239,83,80,0.2)",
                      textcolor="#ef5350", size="small")
            line.new(x1=i, y1=tp_price, x2=end_bar, y2=tp_price,
                     color="#00e676", width=1, style=line.style_dashed)
            label.new(x=i + 2, y=tp_price, text="Take Profit",
                      style=label.style_label_left, color="rgba(0,230,118,0.2)",
                      textcolor="#00e676", size="small")
            box.new(left=i, top=sl_price, right=end_bar, bottom=tp_price,
                    border_color="rgba(239,83,80,0.15)", bgcolor="rgba(239,83,80,0.03)")
