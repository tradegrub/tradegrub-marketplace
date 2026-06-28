from tg_scripting import *
import numpy as np

# --- Inputs ---
reg_length = input.int(50, "Regression Length", minval=20, maxval=200)
poly_degree = input.int(2, "Polynomial Degree", minval=1, maxval=5)
num_bins = input.int(30, "Volume Bins", minval=10, maxval=100)
va_pct = input.float(0.7, "Value Area %", minval=0.5, maxval=0.9)
show_regression = input.bool(True, "Show Regression Line")
show_poc = input.bool(True, "Show Point of Control")

# --- Prepare Data ---
close_arr = np.array(close, dtype=np.float64)
high_arr = np.array(high, dtype=np.float64)
low_arr = np.array(low, dtype=np.float64)
volume_arr = np.array(volume, dtype=np.float64)
n = len(close_arr)

# --- Polynomial Regression on Price ---
x_full = np.arange(n, dtype=np.float64)

# Rolling regression: compute fitted values over the regression window
reg_line = np.full(n, np.nan)
reg_residual = np.full(n, np.nan)
reg_r_squared = np.full(n, np.nan)

for i in range(reg_length, n):
    x_seg = np.arange(reg_length, dtype=np.float64)
    y_seg = close_arr[i - reg_length:i]

    # Polynomial fit using np.polyfit
    coeffs = np.polyfit(x_seg, y_seg, poly_degree)
    fitted = np.polyval(coeffs, x_seg)
    reg_line[i] = fitted[-1]  # current fitted value

    # Residual and R-squared
    ss_res = np.sum((y_seg - fitted) ** 2)
    ss_tot = np.sum((y_seg - np.mean(y_seg)) ** 2)
    reg_r_squared[i] = 1.0 - (ss_res / max(ss_tot, 1e-10))
    reg_residual[i] = y_seg[-1] - fitted[-1]

# --- OLS Linear Regression for Slope/Intercept ---
ols_slope = np.full(n, np.nan)
ols_intercept = np.full(n, np.nan)

for i in range(reg_length, n):
    x_seg = np.arange(reg_length, dtype=np.float64).reshape(-1, 1)
    x_design = np.column_stack([x_seg, np.ones(reg_length)])
    y_seg = close_arr[i - reg_length:i]

    # OLS via np.linalg.lstsq
    result = np.linalg.lstsq(x_design, y_seg, rcond=None)
    beta = result[0]
    ols_slope[i] = beta[0]
    ols_intercept[i] = beta[1]

# --- Regression-Adjusted Volume Profile ---
poc_price = np.full(n, np.nan)
va_high = np.full(n, np.nan)
va_low = np.full(n, np.nan)
vol_concentration = np.full(n, np.nan)

for i in range(reg_length, n):
    seg_high = high_arr[i - reg_length:i]
    seg_low = low_arr[i - reg_length:i]
    seg_close = close_arr[i - reg_length:i]
    seg_vol = volume_arr[i - reg_length:i]

    # Regression-curved price levels
    x_seg = np.arange(reg_length, dtype=np.float64)
    coeffs = np.polyfit(x_seg, seg_close, poly_degree)
    curve_prices = np.polyval(coeffs, x_seg)

    # Distance of each bar from regression curve (normalized)
    deviations = seg_close - curve_prices
    dev_weights = np.exp(-0.5 * (deviations / max(np.std(deviations), 1e-10)) ** 2)

    # Weight volume by proximity to regression curve
    adjusted_vol = seg_vol * dev_weights

    # Bin prices into histogram buckets
    price_min, price_max = np.min(seg_low), np.max(seg_high)
    bin_edges = np.linspace(price_min, price_max, num_bins + 1)
    bin_centers = 0.5 * (bin_edges[:-1] + bin_edges[1:])

    # Distribute adjusted volume into bins using typical price
    typical_prices = (seg_high + seg_low + seg_close) / 3.0
    vol_profile, _ = np.histogram(typical_prices, bins=bin_edges, weights=adjusted_vol)

    # Point of Control: price level with highest volume
    poc_idx = np.argmax(vol_profile)
    poc_price[i] = bin_centers[poc_idx]

    # Value Area: 70% of total volume centered around POC
    total_vol = np.sum(vol_profile)
    if total_vol > 0:
        # Expand outward from POC until va_pct captured
        sorted_idx = np.argsort(vol_profile)[::-1]
        cumvol = np.cumsum(vol_profile[sorted_idx])
        cutoff_count = np.searchsorted(cumvol, total_vol * va_pct) + 1
        va_indices = sorted_idx[:cutoff_count]
        va_low[i] = bin_centers[np.min(va_indices)]
        va_high[i] = bin_centers[np.max(va_indices)]

        # Volume concentration score: how peaked the distribution is
        vol_concentration[i] = vol_profile[poc_idx] / total_vol * num_bins

# --- Regression Bands (1 std dev of residuals) ---
reg_upper = np.full(n, np.nan)
reg_lower = np.full(n, np.nan)
for i in range(reg_length, n):
    residuals = close_arr[i - reg_length:i] - np.polyval(
        np.polyfit(np.arange(reg_length, dtype=np.float64), close_arr[i - reg_length:i], poly_degree),
        np.arange(reg_length, dtype=np.float64)
    )
    std_resid = np.std(residuals)
    reg_upper[i] = reg_line[i] + std_resid
    reg_lower[i] = reg_line[i] - std_resid

# --- Plots ---
if show_regression:
    p1 = plot(reg_line, title="Regression", color="#42A5F5")
    p2 = plot(reg_upper, title="Reg Upper", color="rgba(66,165,245,0.3)")
    p3 = plot(reg_lower, title="Reg Lower", color="rgba(66,165,245,0.3)")
    fill(p2, p3, color="rgba(66,165,245,0.08)")

if show_poc:
    plot(poc_price, title="POC", color="#FF7043", linewidth=2)

plot(va_high, title="VA High", color="rgba(76,175,80,0.6)")
plot(va_low, title="VA Low", color="rgba(255,82,82,0.6)")
plot(np.nan_to_num(vol_concentration, nan=1.0), title="Vol Concentration", color="#AB47BC")
plot(np.nan_to_num(reg_r_squared, nan=0.0) * 100, title="R-Squared %", color="#78909C")
