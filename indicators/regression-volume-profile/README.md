# Regression Volume Profile

The Regression Volume Profile combines polynomial regression analysis with volume distribution to create a curved volume profile that adapts to the prevailing price trend. Traditional volume profiles distribute volume across horizontal price levels, ignoring the trajectory of price. This indicator fits a polynomial curve to price, weights volume by each bar's proximity to the regression line, and distributes the adjusted volume into price bins to produce Point of Control (POC), Value Area High, and Value Area Low levels that follow the market's structural trend rather than treating all price levels equally.

## Conceptual Diagram

```
  Price                    Volume Profile (curved)
   │                        ┌───┐
   │        ╱╲              │   │
   │   ~~~~╱~~╲~~~~  Reg    │   ████  <-- POC
   │  ╱   ╱    ╲   ╲ Line  │  ███
   │ ╱   ╱      ╲   ╲      │ ██      VA High
   │╱   ╱ +band  ╲   ╲     │████     --------
   │   ╱──────────╲        │██████   POC
   │  ╱   -band    ╲       │████     --------
   │ ╱               ╲     │ ███     VA Low
   │╱                  ╲   │  ██
   └───────────────────── t │ █
       Gaussian weighting:  └──────
       bars near curve get
       higher volume weight
```

## How It Works

The indicator begins with a rolling polynomial regression of closing prices over the specified lookback window. At each bar, np.polyfit computes the polynomial coefficients for the degree selected (default quadratic), and np.polyval evaluates the fitted curve. This produces a smooth regression line that captures the prevailing price trajectory -- linear for degree 1, parabolic for degree 2, and increasingly flexible at higher degrees. The R-squared statistic is calculated from the residual sum of squares to measure how well the regression fits the data.

In parallel, an OLS linear regression is computed using np.linalg.lstsq to extract the slope and intercept. The slope provides a clean measure of trend direction and strength, independent of the polynomial curve used for volume distribution. Regression bands are drawn at one standard deviation of the residuals above and below the fitted line, creating a channel that adapts to both trend and volatility.

The core innovation is the regression-adjusted volume distribution. For each bar in the lookback window, the indicator computes the deviation of the actual close from the regression curve, then applies a Gaussian weighting function (np.exp of the squared normalized deviation). Bars that traded near the regression line receive full volume weight, while bars far from the curve receive diminished weight. This means the volume profile emphasizes prices where the market spent time near its structural trend, filtering out spike noise.

The weighted volume is distributed into price bins using np.histogram with the adjusted volume as weights. The bin with the highest accumulated volume becomes the Point of Control -- the price level of maximum agreement between the regression trend and volume activity. Value Area High and Low are computed by expanding outward from the POC until the specified percentage (default 70%) of total adjusted volume is captured, using np.argsort and np.cumsum for efficient cumulative distribution.

A volume concentration score normalizes the POC volume against total volume, indicating how peaked or distributed the profile is. A high concentration suggests strong consensus at the POC, while a low reading indicates diffuse volume with no dominant level. This metric serves as a conviction gauge for support/resistance at the POC.

## Parameters

| Parameter | Default | Range | Description |
|-----------|---------|-------|-------------|
| Regression Length | 50 | 20 - 200 | Number of bars for the regression window |
| Polynomial Degree | 2 | 1 - 5 | Degree of polynomial fit (1=linear, 2=quadratic, etc.) |
| Volume Bins | 30 | 10 - 100 | Number of price levels for volume distribution |
| Value Area % | 0.70 | 0.50 - 0.90 | Proportion of volume defining the Value Area |
| Show Regression Line | true | -- | Display the fitted regression curve and bands |
| Show Point of Control | true | -- | Display the POC price level |

## Python Advantage

The polynomial regression, OLS decomposition, Gaussian-weighted histogram, and cumulative value area calculation require numpy operations that have no equivalent in Pine Script:

```python
# Polynomial regression with arbitrary degree
coeffs = np.polyfit(x_seg, close_seg, poly_degree)
curve = np.polyval(coeffs, x_seg)

# OLS via least squares for slope extraction
x_design = np.column_stack([x_seg.reshape(-1, 1), np.ones(n)])
beta = np.linalg.lstsq(x_design, y_seg, rcond=None)[0]

# Gaussian-weighted volume: bars near regression get more weight
deviations = close_seg - curve
weights = np.exp(-0.5 * (deviations / np.std(deviations)) ** 2)
adjusted_vol = volume_seg * weights

# Histogram-based volume profile with weighted bins
vol_profile, _ = np.histogram(typical_prices, bins=edges, weights=adjusted_vol)
poc_idx = np.argmax(vol_profile)

# Value area via cumulative sorted distribution
sorted_idx = np.argsort(vol_profile)[::-1]
cumvol = np.cumsum(vol_profile[sorted_idx])
cutoff = np.searchsorted(cumvol, total_vol * 0.70) + 1
```

Pine Script cannot perform polynomial fitting, matrix least squares, Gaussian kernel weighting, arbitrary histogramming, or cumulative sorted distributions. This indicator requires the full numpy linear algebra and statistics stack.

## When to Use

The Regression Volume Profile is most effective on daily and weekly charts for swing and position trading, where the volume profile has enough data to produce meaningful distributions. It works well on liquid equities, ETFs, and futures where volume data is reliable. Use it during trending markets to find support/resistance levels that respect the trend's trajectory, and during consolidation to identify where volume is concentrating before a breakout. The POC is particularly useful as a mean-reversion target in ranging markets, while the regression bands serve as trend-following channels.

## Risk Management

The polynomial degree significantly affects sensitivity: degree 1 (linear) provides the most stable signals but misses curvature, while degrees 4-5 overfit to noise and should be used only on higher timeframes with large lookback windows. Always cross-reference the R-squared reading -- values below 0.3 indicate poor regression fit, meaning the POC and Value Area levels are less reliable. Place stops beyond the Value Area boundaries rather than exactly at them, as these levels attract liquidity sweeps. The volume concentration score below 1.0 suggests the profile is flat and the POC may not hold as support/resistance.

## Combining with Other Indicators

- Layer with VWAP to compare the regression-adjusted POC against the anchored VWAP -- convergence of both levels creates high-conviction support/resistance zones.
- Use alongside RSI or Stochastics to time entries when price reaches the VA High or VA Low with momentum confirmation.
- Pair with ATR Percent to gauge whether the regression bands are wide (volatile) or narrow (compressed), adjusting position size accordingly.
