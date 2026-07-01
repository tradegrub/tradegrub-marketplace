# Volume Profile POC

The Volume Profile POC (Point of Control) constructs a horizontal volume profile by distributing traded volume into price bins across the lookback period, then identifies the price level where the most volume was transacted. The POC acts as a magnet for price, representing the "fair value" where the most trading activity occurred. The Value Area High (VAH) and Value Area Low (VAL) define the range containing the configured percentage of total volume, providing institutional-grade support and resistance levels derived from actual transaction data.

## Conceptual Diagram

![Concept](concept.svg)

## How It Works

The indicator divides the price range (highest high to lowest low over the lookback period, default 100 bars) into equal-sized rows (default 24). For each historical bar, the midpoint of that bar's high-low range is computed, and the bar's volume is assigned to the corresponding price row. This builds a volume histogram across price levels.

The Point of Control is the row with the highest accumulated volume. Its price level is calculated as the center of that row: `price_low + (poc_idx + 0.5) * row_height`. The POC represents the price where the most trading activity occurred, the consensus "fair value" price for the lookback period.

The Value Area is computed by expanding outward from the POC row. Starting with the POC's volume, the algorithm compares the adjacent rows above and below and adds the larger one, continuing until the cumulative volume reaches the configured percentage (default 70%) of total volume. The upper boundary becomes the Value Area High (VAH) and the lower boundary becomes the Value Area Low (VAL).

Price tends to spend the majority of time within the Value Area and gravitates toward the POC. Moves outside the Value Area that fail to sustain indicate rejection and likely return to the POC. Moves outside the Value Area that sustain with volume indicate a genuine shift in value and a potential new POC formation.

## Parameters

| Parameter | Default | Range | Description |
|-----------|---------|-------|-------------|
| Lookback Bars | 100 | 10 - 500 | Number of bars over which to build the volume profile |
| Row Count | 24 | 10 - 100 | Number of price bins for volume distribution |
| Value Area % | 70.0 | 50.0 - 90.0 | Percentage of total volume defining the Value Area |

## Python Advantage

The volume profile construction uses Python for-loops with list operations and dynamic index arithmetic that would be extremely cumbersome in Pine's limited loop constructs:

```python
# Build volume histogram using Python list and loop
vol_bins = [0.0] * rows
for i in range(lookback):
    bar_mid = (high[i] + low[i]) / 2
    bin_idx = int((bar_mid - price_low) / row_height)
    bin_idx = min(bin_idx, rows - 1)
    vol_bins[bin_idx] += volume[i]

# POC: price level of the highest-volume bin
poc_idx = vol_bins.index(max(vol_bins))
poc_price = price_low + (poc_idx + 0.5) * row_height

# Value Area expansion using Python while-loop with bidirectional scan
cum_vol = vol_bins[poc_idx]
lo_idx = poc_idx
hi_idx = poc_idx
while cum_vol < target_vol:
    expand_lo = vol_bins[lo_idx - 1] if lo_idx > 0 else 0
    expand_hi = vol_bins[hi_idx + 1] if hi_idx < rows - 1 else 0
    if expand_lo >= expand_hi and lo_idx > 0:
        lo_idx -= 1
        cum_vol += vol_bins[lo_idx]
    elif hi_idx < rows - 1:
        hi_idx += 1
        cum_vol += vol_bins[hi_idx]
    else:
        break
```

The bidirectional Value Area expansion algorithm uses Python's full-featured `while` loop with conditional boundary checking, `int()` casting for bin indexing, and list methods like `.index(max(...))`. Pine's `for` loops have strict iteration limits and lack dynamic break conditions. The Python implementation handles edge cases (bin boundaries, uneven distributions) cleanly with standard conditional logic.

## When to Use

Volume Profile POC works best on liquid instruments with reliable volume data: equities, ETFs, and futures. Use it on daily charts to identify multi-week value areas for swing trading, or on intraday charts (5-minute, 15-minute) for session-level POC and Value Area levels. The POC and Value Area are especially powerful during range-bound markets where price oscillates around the fair value level.

## Risk Management

When entering near the POC, set stops just beyond the Value Area boundary on the opposite side. The Value Area itself defines the risk: if price breaks through VAH or VAL with volume, the profile structure has changed and the trade thesis is invalidated. During trending markets, the POC may lag significantly behind current price; do not use stale POC levels as support/resistance when the market has clearly shifted to a new value area.

## Combining with Other Indicators

- **Fibonacci Bands**: When Fibonacci retracement levels align with the POC or Value Area boundaries, the confluence of structural and volume-based levels creates exceptionally strong support/resistance.
- **VWAP StdDev Bands**: Compare the POC with VWAP for two independent fair-value estimates. When they converge, the price level has strong significance from both volume-weighted and profile-based perspectives.
- **Smart Money Concepts**: Look for Fair Value Gaps that overlap with the Value Area for high-probability mean-reversion entries backed by both structural imbalance and volume concentration.
