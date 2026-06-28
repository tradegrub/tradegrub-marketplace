from tg_scripting import *

rsi_len = input.int(14, "RSI Length", minval=5, maxval=50)
cci_len = input.int(20, "CCI Length", minval=5, maxval=50)
stoch_len = input.int(14, "Stochastic Length", minval=5, maxval=50)
signal_len = input.int(5, "Signal Length", minval=2, maxval=20)

import numpy as np

rsi_val = ta.rsi(close, rsi_len)
rsi_norm = (rsi_val - 50) / 50

cci_val = ta.cci(close, cci_len)
cci_norm = np.clip(cci_val / 200, -1, 1)

stoch_val = ta.stoch(high, low, close, stoch_len)
stoch_norm = (stoch_val - 50) / 50

composite = (rsi_norm + cci_norm + stoch_norm) / 3 * 100
signal = ta.sma(composite, signal_len)

plot(composite, title="Momentum Composite", color="#7E57C2")
plot(signal, title="Signal", color="#FF8A65")
hline(50, title="Overbought", color="rgba(239,83,80,0.5)")
hline(-50, title="Oversold", color="rgba(38,166,154,0.5)")
hline(0, title="Zero", color="rgba(128,128,128,0.3)")

bgcolor(composite > 50, color="rgba(239,83,80,0.06)")
bgcolor(composite < -50, color="rgba(38,166,154,0.06)")
