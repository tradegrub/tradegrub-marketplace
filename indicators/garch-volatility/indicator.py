from tg_scripting import *
import numpy as np

indicator("GARCH Volatility Forecast", overlay=False)

omega_mult = input.float(0.1, "Omega Weight", minval=0.01, maxval=1.0, step=0.01)
alpha_val = input.float(0.1, "Alpha (Shock)", minval=0.01, maxval=0.5, step=0.01)
beta_val = input.float(0.85, "Beta (Persistence)", minval=0.1, maxval=0.99, step=0.01)
forecast_bars = input.int(5, "Forecast Horizon", minval=1, maxval=20)

src = np.array(close, dtype=float)
n = len(src)

# Log returns
returns = np.zeros(n)
for i in range(1, n):
    if src[i - 1] > 0:
        returns[i] = np.log(src[i] / src[i - 1])

# Unconditional variance
var_uncond = np.var(returns[1:]) if n > 1 else 0.0001
omega = omega_mult * var_uncond * (1 - alpha_val - beta_val)
if omega <= 0:
    omega = 0.00001

# GARCH(1,1) conditional variance
cond_var = np.full(n, var_uncond)
for i in range(2, n):
    cond_var[i] = omega + alpha_val * returns[i - 1] ** 2 + beta_val * cond_var[i - 1]
    cond_var[i] = max(cond_var[i], 1e-10)

# Conditional volatility (annualized approx)
cond_vol = np.sqrt(cond_var) * 100

# Forecast: h-step ahead
forecast_var = np.full(n, var_uncond)
long_run_var = omega / max(1 - alpha_val - beta_val, 0.001)
for i in range(1, n):
    persistence = (alpha_val + beta_val) ** forecast_bars
    forecast_var[i] = long_run_var + persistence * (cond_var[i] - long_run_var)
    forecast_var[i] = max(forecast_var[i], 1e-10)

forecast_vol = np.sqrt(forecast_var) * 100

# Volatility regime
vol_sma = ta.sma(cond_vol.tolist(), 20)
vol_sma_arr = np.array(vol_sma, dtype=float)
high_vol = np.array([cond_vol[i] > vol_sma_arr[i] * 1.5 if not np.isnan(vol_sma_arr[i]) else False for i in range(n)])

plot(cond_vol.tolist(), title="Conditional Vol", color="#42A5F5", linewidth=2)
plot(forecast_vol.tolist(), title="Forecast Vol", color="#FFA726", linewidth=1)
plot(vol_sma_arr.tolist(), title="Vol SMA(20)", color="#888888", linewidth=1)
bgcolor(high_vol, color="rgba(239,83,80,0.08)")
