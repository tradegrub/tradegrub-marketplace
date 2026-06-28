# Doji Reversal Strategy
from tg_scripting import *

atr_len = input.int(14, "ATR Length", minval=5, maxval=50)
atr_mult = input.float(2.0, "ATR Target Multiplier", minval=1.0, maxval=5.0)
doji_pct = input.float(0.05, "Doji Body % of Range", minval=0.01, maxval=0.15)
sr_len = input.int(20, "Support/Resistance Lookback", minval=10, maxval=50)

atr = ta.atr(high, low, close, atr_len)
support = ta.lowest(low, sr_len)
resistance = ta.highest(high, sr_len)

body = np.abs(close - open)
candle_range = high - low
body_pct = np.where(candle_range > 0, body / candle_range, 1.0)

is_doji = body_pct[-1] <= doji_pct

# Near support: potential bullish reversal
near_support = (low[-1] - support[-1]) < atr[-1] * 0.3
# Near resistance: potential bearish reversal
near_resistance = (resistance[-1] - high[-1]) < atr[-1] * 0.3

# Confirm with next bar direction
prev_doji_bull = body_pct[-2] <= doji_pct and (low[-2] - support[-2]) < atr[-2] * 0.3
prev_doji_bear = body_pct[-2] <= doji_pct and (resistance[-2] - high[-2]) < atr[-2] * 0.3

bull_confirm = prev_doji_bull and close[-1] > open[-1]
bear_confirm = prev_doji_bear and close[-1] < open[-1]

if bull_confirm:
    strategy.entry("Long", strategy.LONG)
    strategy.exit("Long Exit", "Long", stop=low[-2] - atr[-1] * 0.5,
                  limit=close[-1] + atr[-1] * atr_mult)

if bear_confirm:
    strategy.entry("Short", strategy.SHORT)
    strategy.exit("Short Exit", "Short", stop=high[-2] + atr[-1] * 0.5,
                  limit=close[-1] - atr[-1] * atr_mult)

plot(support, title="Support", color="green")
plot(resistance, title="Resistance", color="red")
plot(body_pct, title="Body Pct", color="blue")
hline(doji_pct, title="Doji Threshold", color="gray")
plotshape(bull_confirm, title="Bull Doji", style="triangleup", location="belowbar", color="green")
plotshape(bear_confirm, title="Bear Doji", style="triangledown", location="abovebar", color="red")
