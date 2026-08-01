from tg_scripting import *
import numpy as np

indicator("Oscillator Channel Overlay", overlay=True)

reg_length = input.int(50, "Regression Length", minval=10, maxval=200)
rsi_length = input.int(14, "RSI Length", minval=2, maxval=50)

src = np.array(close, dtype=float)
hi = np.array(high, dtype=float)
lo = np.array(low, dtype=float)
n = len(src)

rsi_vals = np.array(ta.rsi(close, rsi_length), dtype=float)
atr_vals = np.array(ta.atr(high, low, close, reg_length), dtype=float)

reg_line = np.full(n, np.nan)
upper_channel = np.full(n, np.nan)
lower_channel = np.full(n, np.nan)
rsi_mapped = np.full(n, np.nan)

for i in range(reg_length, n):
    window = src[i - reg_length:i + 1]
    x = np.arange(len(window), dtype=float)

    # Linear regression using numpy lstsq
    A = np.column_stack([x, np.ones(len(x))])
    coeffs = np.linalg.lstsq(A, window, rcond=None)[0]
    fitted_val = coeffs[0] * float(len(window) - 1) + coeffs[1]

    reg_line[i] = fitted_val

    # Channel width based on ATR
    atr_val = float(atr_vals[i]) if not np.isnan(atr_vals[i]) else 0.0
    channel_width = atr_val * 3.0
    upper_channel[i] = fitted_val + channel_width
    lower_channel[i] = fitted_val - channel_width

    # Map RSI to position within channel
    # RSI 50 = on regression line, RSI 70 = above, RSI 30 = below
    rsi_val = float(rsi_vals[i]) if not np.isnan(rsi_vals[i]) else 50.0
    rsi_offset = (rsi_val - 50.0) / 50.0 * channel_width
    rsi_mapped[i] = fitted_val + rsi_offset

# Color RSI-mapped line by RSI level
rsi_colors = np.where(rsi_vals > 60, "#4CAF50",
             np.where(rsi_vals < 40, "#f44336", "#FF9800")).tolist()

plot(reg_line.tolist(), title="Regression", color="#888888")
plot(upper_channel.tolist(), title="Upper Channel", color="#42a5f580")
plot(lower_channel.tolist(), title="Lower Channel", color="#42a5f580")
plot(rsi_mapped.tolist(), title="RSI Mapped", color=rsi_colors)
