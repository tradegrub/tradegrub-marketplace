# Kalman Filter Trend

The Kalman Filter Trend indicator applies a recursive Bayesian state estimator to price data, producing an optimally smoothed trend line that adapts its responsiveness based on prediction error. Unlike moving averages that apply fixed-weight smoothing, the Kalman filter maintains an internal model of price dynamics (position and velocity), continuously updates its confidence in that model, and adjusts the balance between trusting its prediction versus the new measurement. The result is a trend line that is smooth during steady trends and responsive during regime changes, with statistically grounded confidence bands derived from the filter's own uncertainty estimate.

## Conceptual Diagram

![Concept](concept.svg)

## How It Works

The Kalman filter operates on a predict-update cycle at each bar. In the prediction step, the filter projects the current state (price and optionally velocity) forward using a state transition model. For the constant velocity model, this means the predicted price equals the previous filtered price plus the estimated velocity. The prediction step also propagates the state covariance forward, increasing uncertainty to account for process noise, the inherent unpredictability of price movement.

In the update step, the filter compares its prediction against the actual closing price to compute the innovation (prediction error). The Kalman gain, a matrix derived from the ratio of prediction uncertainty to total uncertainty (prediction plus measurement noise), determines how much weight to give the new measurement. When the filter is confident in its model (low covariance), the gain is small and the filter mostly trusts its prediction. When prediction errors are large, the gain increases and the filter becomes more responsive to new data.

The adaptive noise estimation feature dynamically adjusts measurement noise based on recent innovation variance. If the filter's predictions have been consistently wrong (high innovation variance), it increases the measurement noise parameter, causing the filter to track price more closely. During stable trends where predictions are accurate, the noise estimate decreases and the filter produces smoother output. This is implemented using the innovation covariance identity: the theoretical innovation variance should equal H*P*H^T + R, so R can be backed out from observed innovation statistics.

Confidence bands are derived directly from the state covariance matrix P, specifically the square root of the position variance P[0,0]. This gives statistically meaningful bands: they widen when the filter is uncertain (after regime changes or high volatility) and narrow when the filter has converged on a stable trend. The band width multiplier controls the confidence level, analogous to standard deviation multiples.

Trend reversal signals are generated when the direction of the filtered price changes. Because the Kalman filter already optimally smooths noise, these reversals are significantly more reliable than those derived from moving average crossovers. The optional velocity state provides an additional dimension: positive velocity confirms uptrend momentum, while decelerating velocity can warn of trend exhaustion before the price direction changes.

## Parameters

| Parameter | Default | Range | Description |
|-----------|---------|-------|-------------|
| Process Noise (Q) | 0.01 | 0.0001-1.0 | How much the true price is expected to change between bars; higher values make the filter more responsive |
| Measurement Noise (R) | 1.0 | 0.01-50.0 | Assumed noise in price observations; higher values produce smoother output |
| Confidence Band Multiplier | 2.0 | 0.5-5.0 | Width of confidence bands in covariance units |
| Include Velocity State | true | - | Use 2D state (position + velocity) for momentum-aware filtering |
| Adaptive Noise Estimation | true | - | Dynamically adjust R based on recent prediction accuracy |
| Adaptive Window | 20 | 5-100 | Lookback for innovation variance estimation |

## Python Advantage

The Kalman filter requires matrix algebra that is fundamentally impossible in Pine:

```python
# State prediction with matrix multiplication
x_pred = np.dot(F, x)                          # F is 2x2 transition matrix
P_pred = np.dot(np.dot(F, P), F.T) + Q         # Covariance propagation

# Kalman gain via matrix inversion
S = np.dot(np.dot(H, P_pred), H.T) + R         # Innovation covariance
S_inv = np.linalg.inv(S)                        # Matrix inversion
K = np.dot(np.dot(P_pred, H.T), S_inv)         # Optimal gain

# Joseph form covariance update (numerically stable)
IKH = np.eye(dim) - np.dot(K, H)
P = np.dot(np.dot(IKH, P_pred), IKH.T) + np.dot(np.dot(K, R, K.T))

# Adaptive R from innovation statistics
innovation_var = np.var(recent_innovations)
R_adaptive = max(0.01, innovation_var - predicted_var)
```

Pine has no matrix types, no np.dot, no np.linalg.inv, and no way to maintain and propagate a covariance matrix. Any approximation would lose the mathematical guarantees that make the Kalman filter optimal.

## When to Use

The Kalman filter excels on any instrument and timeframe where you want trend identification with minimal lag and statistically grounded confidence. It is particularly effective on forex pairs and futures where price behavior approximates a random walk with drift, matching the filter's underlying assumptions. Use it on 1-hour to weekly charts for trend following, on lower timeframes for mean reversion when price deviates beyond the confidence bands, and as a replacement for moving averages in any system where lag reduction matters.

## Risk Management

The Q/R ratio is the critical tuning parameter. Too high a Q relative to R makes the filter track noise; too low makes it sluggish. Start with defaults and adjust Q upward for more responsive tracking or R upward for smoother output. The confidence bands are not hard boundaries; they represent the filter's internal uncertainty and should be used as probabilistic zones rather than exact levels. Position sizing should account for band width: wider bands indicate higher uncertainty and warrant smaller positions.

## Combining with Other Indicators

- **Volume Profile**: Combine Kalman trend direction with volume confirmation to filter out low-conviction reversals.
- **RSI**: Use RSI divergence against Kalman trend direction to identify potential exhaustion points with higher confidence.
- **Bollinger Bands**: Compare Kalman confidence bands (model-based) against Bollinger Bands (statistical) to identify regimes where the two frameworks agree on volatility.
