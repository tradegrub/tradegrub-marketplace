# Volatility Clustering (DBSCAN)

A machine learning indicator that uses scikit-learn DBSCAN (Density-Based Spatial Clustering of Applications with Noise) to discover natural volatility clusters in market data. Unlike KMeans, DBSCAN does not require specifying the number of clusters in advance and can identify outlier bars as noise, making it well suited for markets where the number of distinct volatility regimes is unknown.

## Conceptual Diagram

![Concept](concept.svg)

## How It Works

The indicator extracts three features at each bar. ATR% measures the average true range as a percentage of price, capturing realized volatility. Return magnitude computes the absolute percentage change over the lookback period, measuring directional movement size. Volume ratio compares current volume to its moving average, detecting participation spikes.

These features are standardized using sklearn StandardScaler and fed into the DBSCAN algorithm. DBSCAN groups bars that are densely packed in feature space into clusters, while labeling isolated bars as noise. The epsilon parameter controls how close points must be to form a cluster, and min_samples sets the minimum cluster size.

Clusters are sorted by their average ATR% so that cluster 0 is always the calmest and higher numbers represent increasingly volatile conditions. A majority-vote smoothing filter reduces cluster flicker. Transition labels mark where the market shifts from one volatility regime to another.

## Parameters

| Parameter | Default | Range | Description |
|-----------|---------|-------|-------------|
| ATR Length | 14 | 5-50 | Lookback for ATR calculation |
| Returns Lookback | 10 | 3-50 | Period for return magnitude feature |
| Volume MA Length | 20 | 5-100 | Moving average length for volume ratio |
| DBSCAN Epsilon | 0.8 | 0.1-3.0 | Maximum distance between points in a cluster |
| Min Samples | 5 | 2-20 | Minimum points required to form a cluster |
| Cluster Smoothing | 3 | 1-10 | Majority-vote window to reduce cluster flicker |
| Show Labels | True | on/off | Toggle cluster transition labels |
| Show Transitions | True | on/off | Toggle centroid summary labels |
| Label Cooldown Bars | 15 | 5-50 | Minimum bars between transition labels |

## Outputs

- **Cluster:** Current cluster assignment (white line, integer values)
- **ATR%:** Average true range as percentage of price (gray line)
- **Cluster reference lines:** Horizontal lines for each discovered cluster
- **Transition labels:** Annotations at cluster change points
- **Centroid summaries:** Feature averages for each cluster displayed near the right edge
- **Noise count:** Total bars classified as noise (outliers)

## Python Advantage

DBSCAN clustering with automatic noise detection requires sklearn and has no Pine equivalent:

```python
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler

features = np.column_stack([atr_pct, ret_mag, vol_ratio])
X = StandardScaler().fit_transform(features[valid_idx])
db = DBSCAN(eps=0.8, min_samples=5)
db.fit(X)
```

DBSCAN discovers the natural number of clusters rather than forcing a predefined count, and bars that do not fit any cluster are labeled as noise rather than being forced into an inappropriate group.

## Usage Notes

- Lower epsilon values create tighter, more distinct clusters but may classify more bars as noise. Higher values merge nearby clusters together.
- Increase min_samples on higher timeframes where you want only well-established regimes to be identified.
- The noise count provides a quality check: if most bars are noise, increase epsilon or decrease min_samples.
- Works on any symbol and timeframe. Liquid instruments with varied volatility conditions produce the most informative clustering results.
- Cluster assignments are descriptive and reflect past behavior. They do not predict future volatility regime changes.
