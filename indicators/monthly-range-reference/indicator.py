from tg_scripting import *
import numpy as np

indicator("Monthly Range Reference", overlay=True)

period = input.int(21, "Monthly Period", minval=15, maxval=30)

hi = np.array(high, dtype=float)
lo = np.array(low, dtype=float)
cl = np.array(close, dtype=float)
n = len(cl)

m_hi = np.zeros(n)
m_lo = np.zeros(n)
m_open = np.zeros(n)
m_mid = np.zeros(n)

for i in range(period, n):
    m_hi[i] = np.max(hi[i-period:i+1])
    m_lo[i] = np.min(lo[i-period:i+1])
    m_open[i] = cl[i-period]
    m_mid[i] = (m_hi[i] + m_lo[i]) / 2

trend_down = (cl < m_mid) & (m_mid > 0)
upper_half = (cl > m_mid) & (cl < m_hi) & (m_mid > 0)
near_high = (m_hi > 0) & ((m_hi - cl) / np.maximum(m_hi - m_lo, 1e-10) < 0.1)

plot(m_hi.tolist(), title="Monthly High", color="#4CAF50", linewidth=1)
plot(m_lo.tolist(), title="Monthly Low", color="#f44336", linewidth=1)
plot(m_open.tolist(), title="Monthly Open", color="#42a5f5", linewidth=1)
plot(m_mid.tolist(), title="Monthly Mid", color="#888888", linewidth=1)

bgcolor(trend_down.tolist(), color="rgba(244,67,54,0.04)")
