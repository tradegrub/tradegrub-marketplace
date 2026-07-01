from tg_scripting import *
import numpy as np

indicator("Volume Zone Oscillator", overlay=False)

length = input.int(14, "Length", minval=2, maxval=100)
smooth_len = input.int(3, "Smoothing", minval=1, maxval=20)
ob_level = input.float(40.0, "Overbought", minval=10.0, maxval=80.0, step=5.0)
os_level = input.float(-40.0, "Oversold", minval=-80.0, maxval=-10.0, step=5.0)

close_arr = np.array(close, dtype=float)
vol_arr = np.array(volume, dtype=float)
n = len(close_arr)

price_change = np.zeros(n)
price_change[1:] = np.sign(close_arr[1:] - close_arr[:-1])

directed_vol = vol_arr * price_change

up_vol = np.where(directed_vol > 0, directed_vol, 0.0)
down_vol = np.where(directed_vol < 0, np.abs(directed_vol), 0.0)

up_sum = ta.sma(up_vol.tolist(), length)
down_sum = ta.sma(down_vol.tolist(), length)
total_sum = ta.sma(vol_arr.tolist(), length)

up_arr = np.array(up_sum, dtype=float)
down_arr = np.array(down_sum, dtype=float)
total_arr = np.array(total_sum, dtype=float)

vzo = np.where(total_arr != 0, ((up_arr - down_arr) / total_arr) * 100.0, 0.0)

vzo_smooth = ta.sma(vzo.tolist(), smooth_len)

ob = (np.array(vzo_smooth, dtype=float) > ob_level).tolist()
os_sig = (np.array(vzo_smooth, dtype=float) < os_level).tolist()

plot(vzo.tolist(), title="VZO Raw", color="#42A5F5", linewidth=1)
plot(vzo_smooth, title="VZO", color="#FFA726", linewidth=2)
hline(0.0, title="Zero", color="#555555", linestyle="dashed")
hline(ob_level, title="Overbought", color="#ff1744", linestyle="dashed")
hline(os_level, title="Oversold", color="#00e676", linestyle="dashed")
bgcolor(ob, color="rgba(255,23,68,0.06)")
bgcolor(os_sig, color="rgba(0,230,118,0.06)")
