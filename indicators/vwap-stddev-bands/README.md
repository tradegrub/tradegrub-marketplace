# VWAP StdDev Bands

The VWAP StdDev Bands indicator plots the Volume-Weighted Average Price with standard deviation bands above and below, creating a statistically grounded channel around the volume-weighted fair value. Unlike simple moving average bands, VWAP incorporates volume into the price calculation, giving more weight to prices where heavy trading occurred. The standard deviation bands then define statistically significant deviations from this volume-weighted mean, providing objective overbought and oversold levels.

## Conceptual Diagram

```text
Price
 │    ·  · Upper Band ·  ·  ·  ·
 │   · ╱╲ ·        · ╱╲·
 │  ·╱   ╲·  ════ ·╱   ╲·
 │ ·╱  ╱╲  ╲·    ·╱     ╲·
 │·╱  ╱  ╲  ╲·  ·╱       ╲·
 │╱──╱────╲──╲──╱─── VWAP ──╲──
 │  ╱      ╲  ╲╱             ╲
 │ ·  · Lower Band ·  · · · · ·╲
 │╱         ╲                    ╲
 │           ╲        Price      ╲
 │            ╲      returns to   ╲
 │             ╲     VWAP          ╲
 └──────────────────────────────── Time
   Touch upper   Mean reversion   Touch lower
   (sell zone)   to VWAP          (buy zone)
```

## How It Works

The indicator first computes VWAP using the high, low, close, and volume data. VWAP weights each price bar by its volume, so bars with heavy trading pull the average more than light-volume bars. This creates a "true" average price that reflects where the most actual trading occurred rather than simply averaging closing prices.

The standard deviation of the close price is calculated over a configurable period (default 14 bars) and multiplied by the user-specified multiplier (default 2.0). The upper band is VWAP plus this deviation, and the lower band is VWAP minus this deviation. Under normal distribution assumptions, approximately 95% of price observations should fall within 2 standard deviations of the mean.

The area between the upper and lower bands is filled with translucent color to create a visual channel. When the bands are narrow, price is consolidating tightly around VWAP. When they widen, volatility is expanding and price is making larger deviations from the volume-weighted mean.

Price touching or penetrating the upper band indicates the asset is trading significantly above its volume-weighted fair value, a potential mean-reversion short or profit-taking zone. Price touching the lower band indicates it is trading significantly below fair value, a potential mean-reversion long entry. The VWAP line itself acts as the equilibrium target for mean-reversion trades.

## Parameters

| Parameter | Default | Range | Description |
|-----------|---------|-------|-------------|
| Length | 14 | 1 - 200 | Lookback period for standard deviation calculation |
| StdDev Multiplier | 2.0 | 0.5 - 5.0 | Number of standard deviations for band width |

## Python Advantage

The VWAP and band computation chain combines volume-weighted averaging with statistical deviation in clean vectorized operations:

```python
# VWAP computed from full OHLCV arrays
vwap_val = ta.vwap(high, low, close, volume)

# Standard deviation bands around VWAP
basis = ta.sma(close, length)
dev = mult * ta.stdev(close, length)
upper = vwap_val + dev
lower = vwap_val - dev

# Single fill call creates the entire band visualization
fill(upper, lower, color="rgba(38,166,154,0.08)")
```

The band computation `vwap_val + dev` adds two full arrays element-wise, producing the entire upper band series in one operation. Python makes it trivial to add additional band levels (e.g., `upper_2 = vwap_val + 2 * dev` and `upper_3 = vwap_val + 3 * dev`) for multi-tier probability zones, or compute `(close - vwap_val) / dev` for a VWAP-relative z-score across the entire history.

## When to Use

VWAP StdDev Bands are most effective on intraday timeframes (1-minute through 1-hour) where VWAP has the strongest institutional relevance, as many large funds benchmark their execution against VWAP. They also work on daily charts for swing trading. The indicator performs best on liquid instruments with reliable volume data: equities, ETFs, and futures. It is especially useful for mean-reversion strategies where price oscillates around fair value.

## Risk Management

For mean-reversion entries at the bands, set stops just beyond the band by a small buffer (e.g., 0.5 ATR beyond the band). If price closes beyond the band and sustains, the mean-reversion thesis is failing and the market may be trending away from VWAP. During strong trends, price can ride along the upper or lower band for extended periods without reverting, so do not blindly fade band touches in trending environments. Confirm band touches with momentum indicators before entering.

## Combining with Other Indicators

- **Volume Profile POC**: Compare VWAP with the POC for two independent estimates of fair value. When they converge, the price level carries exceptional significance.
- **Z-Score Indicator**: Apply the Z-Score to the close-minus-VWAP series for a statistically rigorous measure of how extended price is from volume-weighted fair value.
- **Momentum Composite**: Confirm band touch entries with the Momentum Composite to avoid fading strong momentum that may push price through the band.
