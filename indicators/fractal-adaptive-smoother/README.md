# Fractal Adaptive Smoother

A self-tuning price smoother that measures the fractal dimension of price action to automatically adjust its responsiveness. In trending markets (low fractal dimension), the smoother becomes fast and responsive. In choppy, mean-reverting markets (high fractal dimension), it applies heavy smoothing to filter noise. Includes adaptive volatility bands that widen and contract based on market regime.

## Conceptual Diagram

```
Price ~~~~~~/\/\/\/\~~~~~~        Choppy (FD ~1.7)
              |                    Heavy smoothing applied
              v
Smooth -------.....------         Filtered output

Price ------/----------/-----     Trending (FD ~1.2)
              |                    Light smoothing applied
              v
Smooth -----/----------/----      Responsive output

FD:    1.0 |===TREND===|===MID===|===CHOP===| 2.0
            1.0       1.35      1.65       2.0
                        |         |
                   Green BG    Red BG

Bands:  ----=====[Smooth]=====----
        Wider in trends, tighter in chop
```

## How It Works

The indicator computes the fractal dimension (FD) of price over a rolling window. Fractal dimension quantifies the "roughness" of a time series on a scale from 1.0 (perfectly smooth trend) to 2.0 (completely random, space-filling noise). This mathematical property captures market regime far more precisely than simple volatility measures.

Two fractal estimation methods are available. The Higuchi method constructs curve lengths at multiple scales by subsampling the series at increasing intervals, then fits a log-log regression to estimate the scaling exponent. The box-counting method tiles the normalized price series with boxes at multiple resolutions and counts occupied boxes, with the scaling slope giving the fractal dimension. Both produce values between 1.0 and 2.0.

The fractal dimension drives an adaptive alpha parameter for exponential smoothing. When FD is low (trending), alpha is large, making the smoother track price closely. When FD is high (choppy), alpha shrinks, applying aggressive filtering. This creates a single smoothed line that automatically adjusts its lag based on market structure.

Adaptive volatility bands surround the smoothed line using the root-mean-square deviation of price from the smoother. Band width is further scaled by the fractal regime: bands expand during trends to capture directional moves, and contract during chop to define mean-reversion boundaries. Background coloring highlights the current regime.

## Parameters

| Parameter | Default | Range | Description |
|-----------|---------|-------|-------------|
| Fractal Period | 50 | 10-200 | Lookback window for fractal dimension calculation |
| Base Smoothing Alpha | 0.1 | 0.01-0.5 | Minimum smoothing factor (lower = more smoothing) |
| Band Multiplier | 2.0 | 0.5-5.0 | Width multiplier for adaptive volatility bands |
| Method | 1 | 1-2 | Fractal estimation method (1: Higuchi, 2: Box-counting) |

## Python Advantage

The fractal dimension calculation requires nested loops, log-log regression, and dynamic array construction that cannot be expressed in Pine Script:

```python
# Higuchi fractal dimension: multi-scale curve length estimation
ks = np.arange(1, k_max + 1)
lengths = np.zeros(k_max)
for k in ks:
    for m in range(1, k + 1):
        indices = np.arange(m - 1, n, k)
        seg = series[indices]
        diffs = np.abs(np.diff(seg))
        norm = (n - 1) / (k * len(diffs)) * np.sum(diffs)
        seg_lengths.append(norm)
    lengths[k - 1] = np.nanmean(seg_lengths)

# Log-log regression for fractal dimension
log_k = np.log(1.0 / ks[valid])
log_l = np.log(lengths[valid])
slope, _ = np.polyfit(log_k, log_l, 1)  # FD = slope

# Adaptive alpha derived from fractal dimension
adaptive_alpha = np.clip(smooth_base / (alpha_range + smooth_base), 0.01, 1.0)
```

This multi-scale analysis with arbitrary subsampling, dynamic array sizes, and least-squares fitting is impossible in Pine Script, which lacks array indexing with computed strides, regression functions on arbitrary data, and nested iteration.

## When to Use

Best applied on daily and 4-hour charts for swing trading, where regime changes are meaningful. Works well on liquid markets (major forex pairs, index futures, large-cap stocks) where fractal properties are well-defined. The Higuchi method is more computationally stable; box-counting works better on very noisy data. Use shorter periods (10-20) for intraday scalping, longer periods (100-200) for position trading.

## Risk Management

The fractal dimension is a lagging measure by nature since it requires a full window of data. Regime transitions appear with delay, so avoid relying on the indicator alone for entries. The adaptive bands are not hard stop levels. During regime transitions (FD crossing 1.5), the smoother may whipsaw as it adjusts speed. Use fixed stop-losses independent of the indicator, and reduce position size when FD is near 1.5 (ambiguous regime).

## Combining with Other Indicators

- Pair with RSI or Stochastic for mean-reversion entries when the fractal dimension signals choppy regime (FD > 1.65), using the adaptive bands as targets
- Combine with ADX to confirm trending signals: low FD plus high ADX gives strong trend conviction for breakout or momentum strategies
- Use alongside volume profile or VWAP to distinguish genuine regime shifts from low-volume drift
