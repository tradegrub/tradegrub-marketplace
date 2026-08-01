# Savitzky-Golay Peak Reversal

Uses scipy.signal.argrelextrema to mathematically detect local peaks and troughs in price data, then trades confirmed reversals away from those extrema. Unlike moving average crossovers that lag by design, this approach identifies the actual turning points in the high/low series and waits for price to confirm the reversal before entering.

## Conceptual Diagram

![Concept](concept.svg)

## How It Works

The strategy feeds the high array into argrelextrema with np.greater_equal to find swing highs, and the low array with np.less_equal to find swing lows. The "order" parameter controls how many bars on each side must be lower (for peaks) or higher (for troughs) to qualify as a local extremum. Higher order values filter out minor wiggles and only flag significant turning points.

After a trough is detected, the strategy waits for a configurable number of confirmation bars, then checks whether price has moved a minimum percentage above the trough level while also closing higher than the previous bar. When both conditions are met, a long entry fires. The mirror logic applies for peaks and short entries.

Risk management uses ATR-based stops and take profit targets. The stop is placed a multiple of ATR below the entry for longs (above for shorts), and the take profit is set at a configurable ratio of that stop distance.

## Parameters

| Parameter | Default | Range | Description |
|-----------|---------|-------|-------------|
| Peak Order | 5 | 2-20 | Bars on each side required to confirm a local extremum |
| ATR Length | 14 | 5-50 | Period for Average True Range calculation |
| ATR Stop Multiple | 2.0 | 1.0-5.0 | Stop loss distance as a multiple of ATR |
| Take Profit Ratio | 2.5 | 1.0-5.0 | Take profit as a multiple of the stop distance |
| Min Swing % | 0.5 | 0.1-5.0 | Minimum percentage move from the extremum before entry |
| Confirmation Bars | 2 | 1-5 | Bars to wait after a detected peak/trough before looking for entry |

## Python Advantage

Scipy provides production-grade signal processing that would require extensive manual implementation:

```python
from scipy.signal import argrelextrema

peaks = argrelextrema(high, np.greater_equal, order=5)[0]
troughs = argrelextrema(low, np.less_equal, order=5)[0]
```

The argrelextrema function handles all boundary conditions and returns clean index arrays of confirmed turning points in a single call.

## When to Use

This strategy works best on instruments with clear swing patterns on 1-hour to daily timeframes. Increase the peak order for noisier instruments or lower timeframes to filter out false reversals. The minimum swing percentage filter adds a second layer of noise reduction beyond what the order parameter provides.

## Risk Management

The confirmation delay means entries happen after the turn has started, so some of the move is already consumed. Size positions to account for the ATR-based stop distance. The take profit ratio should be at least 2:1 to compensate for the inherent lag in peak detection.

## Combining with Other Indicators

- **Volume Climax Alert**: Volume spikes at detected peaks add conviction to reversal signals
- **Momentum Rank**: Enter only when momentum confirms the direction change
- **Consolidation Quality Score**: High-quality consolidation following a peak suggests the reversal has staying power
