# Market Regime Detector

The SK-Learn Regime Detector uses scikit-learn KMeans clustering to automatically classify market conditions into distinct regimes: trending, ranging, and volatile. Rather than relying on fixed thresholds, the indicator extracts four features per bar (ATR%, absolute returns, volume ratio, and return volatility) and lets the clustering algorithm discover natural groupings in the data.

## Conceptual Diagram

![Concept](concept.svg)

## How It Works

The indicator computes four features at each bar. ATR% measures the average true range as a percentage of price, capturing realized volatility. Absolute returns over the lookback period capture directional momentum magnitude. Volume ratio compares current volume to its moving average, identifying participation spikes. Return volatility (rolling standard deviation of returns) measures how erratic price action has been.

These features are standardized using sklearn StandardScaler and fed into KMeans clustering. The algorithm partitions all bars into N regimes based on feature similarity. Clusters are then sorted by combined volatility metrics so that regime 0 is always the calmest (trending) and the highest regime number is always the most volatile. A majority-vote smoothing filter reduces regime flicker on noisy data.

## Parameters

| Parameter | Default | Range | Description |
|-----------|---------|-------|-------------|
| ATR Length | 14 | 5 - 50 | Lookback for ATR calculation |
| Returns Lookback | 10 | 3 - 50 | Period for return and volatility features |
| Volume MA Length | 20 | 5 - 100 | Moving average length for volume ratio |
| Number of Regimes | 3 | 2 - 5 | How many clusters KMeans should find |
| Regime Smoothing | 3 | 1 - 10 | Majority-vote window to reduce regime flicker |
| Label Cooldown Bars | 15 | 5 - 50 | Minimum bars between regime change labels |
| Show Labels | true | -- | Toggle regime change annotations |
| Show Levels | true | -- | Toggle cluster centroid summary boxes |

## Python Advantage

KMeans clustering, feature standardization, and centroid analysis require sklearn and numpy. These operations have no equivalent in Pine:

```python
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

features = np.column_stack([atr_pct, abs_returns, vol_ratio, ret_volatility])
X = StandardScaler().fit_transform(features[valid_idx])
km = KMeans(n_clusters=3, n_init=10, random_state=42)
km.fit(X)
```

The algorithm adapts to each instrument automatically. A stock with naturally high ATR% will not be mislabeled as volatile simply because of its price characteristics. The clustering finds the natural breakpoints for that specific instrument and timeframe.

## When to Use

Use on daily or 4-hour charts for swing trading regime awareness. The indicator works best on liquid instruments with at least 200 bars of history. Trending regimes favor momentum and breakout strategies. Ranging regimes favor mean-reversion and support/resistance plays. Volatile regimes call for reduced position size and wider stops.

## Risk Management

Regime detection is descriptive, not predictive. A bar classified as "trending" reflects recent behavior, not a guarantee that the trend will continue. Always combine regime context with direct price action analysis and proper position sizing. Reduce exposure during volatile regimes and avoid counter-trend entries during strong trending periods.

## Combining with Other Indicators

- **ADX trend strength:** Use ADX to confirm that trending regimes identified by the detector have genuine directional strength rather than just low-volatility drift.
- **Bollinger Bands:** In ranging regimes, Bollinger Band bounces have higher success rates. In trending regimes, ride the band walk instead of fading it.
- **ATR position sizing:** Scale position size inversely with the regime volatility level. Trending (calm) regimes support larger positions while volatile regimes demand smaller exposure.
- **RSI and mean-reversion indicators:** Enable mean-reversion strategies only during ranging regimes, where overbought and oversold signals have the highest hit rate.
