# Supertrend + ATR + Volume Filter

The Trend Volatility Combo strategy layers three complementary filters: Supertrend for trend direction, ATR for adaptive stop-loss placement, and a volume threshold to confirm that trend changes are backed by genuine participation. By requiring above-average volume at the moment a Supertrend flip occurs, the strategy filters out the low-conviction, noise-driven direction changes that generate most whipsaw losses.

## Conceptual Diagram

```
Price
 |                /\
 |    /\    VOL  /  \     VOL
 |   /  \   ||  /    \    ||
 |  /    \  || /      \   ||
 | /      \/||/        \  ||
 |/ ═══════╗|          ═══╗
 |         ╚══════════════╝  Supertrend
 +──────────────────────────────── Time
Volume
 |   ____    ||  ____       ||
 |  |    |   || |    |      ||
 |__|    |___||_|    |______||__  Avg
 +──────────────────────────────── Time
            BUY             SELL
        (ST flip bull    (ST flip bear
         + vol > avg)     + vol > avg)
```

## How It Works

The Supertrend indicator creates a trailing support/resistance line that flips between bullish and bearish based on ATR-scaled bands. This strategy detects the exact bar where the flip occurs using numpy's `np.roll()` function to compare the current direction state with the previous bar's state.

The volume filter requires that the current bar's volume exceeds the simple moving average of volume multiplied by a threshold factor (default 1.2x). This ensures the Supertrend flip is supported by above-average market participation, filtering out false flips that occur during thin trading conditions.

When both conditions align -- a fresh Supertrend direction flip with confirmed volume -- the strategy enters in the new direction. An ATR-based stop-loss is placed at the entry price minus (for longs) or plus (for shorts) the ATR multiplied by the stop multiplier. This adaptive stop widens during volatile conditions and tightens during calm periods.

Background coloring highlights both the current trend state (green/red) and periods of above-average volume, providing visual context for the dual-filter logic.

## Parameters

| Parameter | Default | Range | Description |
|-----------|---------|-------|-------------|
| Supertrend Length | 10 | 5 - 50 | ATR period used by Supertrend for band calculation |
| Supertrend Multiplier | 3.0 | 1.0 - 6.0 | Band width multiplier for Supertrend distance |
| ATR Length | 14 | 2 - 50 | ATR period for stop-loss distance calculation |
| ATR Stop Multiplier | 1.5 | 0.5 - 5.0 | Stop distance as multiple of ATR |
| Volume Average Length | 20 | 5 - 50 | Period for computing average volume |
| Volume Threshold | 1.2 | 1.0 - 5.0 | Volume must exceed average by this factor for confirmation |

## Python Advantage

The strategy uses `np.roll()` for state-transition detection and vectorized boolean masking for multi-condition filtering:

```python
# numpy roll for detecting state transitions (flips)
prev_bullish = np.roll(st_bullish, 1)
prev_bullish[0] = False
st_flip_bull = st_bullish & prev_bearish

# Vectorized volume confirmation across entire history
vol_confirmed = volume > (vol_avg * vol_thresh)

# Compound entry condition — three boolean arrays combined
long_cond = st_flip_bull & vol_confirmed
```

The `np.roll()` function shifts the entire boolean array by one position to create a "previous bar" comparison, enabling flip detection without bar-by-bar loops. The `vol_confirmed` array is computed once across the full dataset. Pine Script has no equivalent to `np.roll()` and must use `[]` history references evaluated one bar at a time.

## When to Use

This strategy works best on instruments with clear trending behavior and reliable volume data: liquid stocks, crypto pairs on major exchanges, and futures contracts. The volume filter is critical on exchanges where low-liquidity periods produce false Supertrend flips. Use on 1-hour to daily charts. Avoid on instruments with sparse or unreliable volume reporting.

## Risk Management

Each entry includes an ATR-based stop-loss, providing defined risk per trade. The volume filter reduces the total number of trades compared to a raw Supertrend, improving the average trade quality. In very volatile markets, the ATR stop may be wide; consider reducing the ATR stop multiplier or adding a maximum dollar-risk cap per trade. The strategy exits only on the opposite signal, so stale positions can persist if volume dries up.

## Combining with Other Indicators

- **Multi-Period Supertrend** adds a slower Supertrend as a trend-direction confirmation layer.
- **Squeeze Momentum** confirms the Supertrend flip coincides with a volatility expansion event.
- **ADX Trend + RSI Momentum Filter** validates the trend strength behind the volume-confirmed flip.
