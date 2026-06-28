# ADX Trend + RSI Momentum Filter

The ADX Trend + RSI Momentum Filter combines the Average Directional Index (ADX) as a trend strength gate with Directional Movement (+DI/-DI) for bias and RSI for momentum confirmation. Developed from Wilder's original Directional Movement System, this triple-layered approach only trades when ADX confirms a strong trend exists, the DI lines agree on direction, and RSI validates momentum alignment, filtering out the choppy markets that destroy most trend-following strategies.

## Conceptual Diagram

```
ADX / DI
 50 |
    |        /\  ADX
 25 |─ ─ ─ /──\─ ─ ─ ─ ─ ─ ─ ─ Threshold
    |  +DI /    \    -DI
    | ──X──      \  ──X──
    |  / \        \/  / \
    | /   \      / \ /   \
  0 +──────────────────────────── Time

RSI
 65 ─ ─ ─╱─ ─ ─ ─ ─ ─ ─ ─ ─ ─ Long Entry Above
    |   ╱  \           /
 50 |──/────\─────────/──────── 
    | /      \       /
 35 ─ ─ ─ ─ ─\─ ─ ─ ─ ─ ─ ─ ─ Short Entry Below
    |          \/
  0 +──────────────────────────── Time
      BUY              SELL
   (ADX>25,           (ADX>25,
    +DI>-DI,           -DI>+DI,
    RSI>65)            RSI<35)
```

## How It Works

The strategy calculates three components from Wilder's Directional Movement System. ADX measures trend strength on a 0-100 scale regardless of direction. When ADX is below the threshold (default 25), the market is considered range-bound and no trades are taken. This single filter eliminates the majority of whipsaw losses that plague trend systems.

When ADX exceeds the threshold, confirming a trend exists, the +DI and -DI lines determine its direction. If +DI is above -DI, the trend is bullish. If -DI is above +DI, the trend is bearish. This provides the directional bias for trade selection.

RSI then confirms momentum alignment. For long entries, RSI must be above a bullish threshold (default 65), confirming upward momentum is strong. For short entries, RSI must be below a bearish threshold (default 35), confirming downward momentum. This prevents entering trends that are losing steam.

The vectorized implementation processes all three conditions across the entire price history simultaneously, iterating through the combined boolean array to fire entries at every qualifying bar.

## Parameters

| Parameter | Default | Range | Description |
|-----------|---------|-------|-------------|
| DI Length | 14 | 2 - 50 | Period for Directional Indicator (+DI/-DI) calculation |
| ADX Length | 14 | 2 - 50 | Smoothing period for ADX value |
| ADX Trend Threshold | 25 | 10 - 50 | Minimum ADX reading to confirm trending conditions |
| RSI Length | 14 | 2 - 50 | Period for RSI calculation |
| RSI Long Entry Above | 65 | 50 - 80 | RSI must exceed this level for long entries |
| RSI Short Entry Below | 35 | 20 - 50 | RSI must be below this level for short entries |

## Python Advantage

The strategy combines three indicator systems into vectorized boolean arrays using element-wise operators:

```python
# Three independent indicator computations
plus_di, minus_di, adx_val = ta.dmi(high, low, close, adx_dilen)
rsi = ta.rsi(close, rsi_len)

# Vectorized triple-condition filtering with & operator
trending = adx_val > adx_thresh
long_cond = trending & (plus_di > minus_di) & (rsi > rsi_ob)
short_cond = trending & (minus_di > plus_di) & (rsi < rsi_os)

# Full-history iteration on pre-computed boolean arrays
for i in range(len(close)):
    if long_cond[i]:
        strategy.entry("Long", strategy.LONG)
```

The `ta.dmi()` function returns three arrays via tuple unpacking in a single call. The `&` operator performs element-wise AND across numpy boolean arrays, creating a composite condition that is True only where all three indicators agree. Pine Script must evaluate these conditions bar-by-bar and cannot pre-compute the full condition array.

## When to Use

This strategy excels on instruments with sustained directional moves: trending commodities, index ETFs during momentum regimes, and forex majors during central bank policy divergence. Daily timeframes provide the most reliable ADX readings. The ADX filter keeps the strategy flat during choppy periods, preserving capital for genuine trends.

## Risk Management

The strategy lacks explicit stop-loss logic, so positions rely on signal reversal to exit. Consider adding ATR-based stops or trailing stops. The ADX threshold is the primary risk control: raising it to 30 or 35 reduces trade frequency but ensures only the strongest trends are traded. Be aware that ADX is a lagging indicator; by the time it exceeds 25, a portion of the trend move has already occurred.

## Combining with Other Indicators

- **Supertrend** provides a trailing stop that automatically follows the trend, adding exit discipline.
- **Squeeze Momentum** confirms that volatility expansion is supporting the ADX trend reading.
- **Triple Moving Average** adds structural trend alignment across three timeframes.
