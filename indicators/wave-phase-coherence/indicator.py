from tg_scripting import *
import numpy as np

indicator("Wave Phase Coherence", overlay=False)

src = np.array(close, dtype=float)
n = len(src)

# RSI at three timeframes
rsi7 = np.array(ta.rsi(close, 7), dtype=float)
rsi14 = np.array(ta.rsi(close, 14), dtype=float)
rsi28 = np.array(ta.rsi(close, 28), dtype=float)

# Normalize each RSI from 0-100 to -1..1
norm7 = (rsi7 - 50.0) / 50.0
norm14 = (rsi14 - 50.0) / 50.0
norm28 = (rsi28 - 50.0) / 50.0

# Coherence: product of all three (positive when aligned)
coherence = norm7 * norm14 * norm28

# Magnitude: sum of absolute values (total energy)
magnitude = np.abs(norm7) + np.abs(norm14) + np.abs(norm28)

coherence = np.nan_to_num(coherence, nan=0.0)
magnitude = np.nan_to_num(magnitude, nan=0.0)

# Strong constructive interference
strong_bull = (coherence > 0.3).tolist()
strong_bear = (coherence < -0.3).tolist()

plot(coherence.tolist(), title="Coherence", color="#26A69A")
plot(magnitude.tolist(), title="Magnitude", color="#7E57C2")
hline(0, title="Zero", color="#555555")
bgcolor(strong_bull, color="rgba(38,166,154,0.08)")
bgcolor(strong_bear, color="rgba(239,83,80,0.08)")
