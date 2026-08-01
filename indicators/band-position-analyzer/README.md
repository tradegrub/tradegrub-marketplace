# Band Position Analyzer

Measures price position within Bollinger, Keltner, and Donchian bands as percentages for cross-band analysis using numpy. This volatility indicator provides quantitative signals that can be applied to any liquid market across all timeframes.

## Conceptual Diagram

![Concept](concept.svg)

## How It Works

The indicator analyzes price data using volatility techniques to produce actionable signals.

Built-in technical functions used: `atr, bb, ema`. These provide the foundation for the indicator's calculations, computed efficiently across the full price history in a single pass.

Core techniques include exponential moving average, ATR, iterative computation, conditional array operations. The computation processes all bars simultaneously using vectorized numpy operations, ensuring consistent results regardless of the dataset size.

Integer parameters control window lengths and thresholds, allowing the indicator to adapt from scalping on short timeframes to position trading on weekly charts. Shorter windows increase sensitivity to recent price action while longer windows provide smoother, more reliable signals.

Float parameters fine-tune sensitivity and scaling factors. Small adjustments to these values can significantly change signal frequency and quality, so test changes on historical data before applying to live trading.

## Parameters

| Parameter | Default | Range | Description |
|-----------|---------|-------|-------------|
| Bollinger Length | 20 | 10 - 50 | Controls bollinger length sensitivity (int) |
| Bollinger Mult | 2.0 | 1.0 - 4.0 | Controls bollinger mult sensitivity (float) |
| Keltner Length | 20 | 10 - 50 | Controls keltner length sensitivity (int) |
| Donchian Length | 20 | 10 - 50 | Controls donchian length sensitivity (int) |

## Signals

- **Bollinger %**: Primary visual output plotted as a continuous line on the chart
- **Keltner %**: Primary visual output plotted as a continuous line on the chart
- **Donchian %**: Primary visual output plotted as a continuous line on the chart
- **Average Position**: Primary visual output plotted as a continuous line on the chart
- **Upper Zone** (80): Reference level for threshold-based decisions
- **Lower Zone** (20): Reference level for threshold-based decisions
- **Mid** (50): Reference level for threshold-based decisions

## Python Advantage

The entire computation runs as vectorized numpy operations, processing all bars simultaneously rather than one at a time:

```python
atr_arr = np.array(ta.atr(high, low, close, kc_len), dtype=float)
ema_arr = np.nan_to_num(ema_arr, nan=0.0)
atr_arr = np.nan_to_num(atr_arr, nan=1.0)
kc_up = ema_arr + 1.5 * atr_arr
kc_lo = ema_arr - 1.5 * atr_arr
kc_range = kc_up - kc_lo
kc_pos = np.where(kc_range > 0, (cl - kc_lo) / kc_range * 100, 50.0)

dc_hi = np.zeros(n)
dc_lo = np.zeros(n)
for i in range(dc_len, n):
```

Python's numpy arrays allow element-wise arithmetic across thousands of bars in a single expression. Adding custom variations or combining with other calculations is straightforward, requiring only standard array operations.

## When to Use

- Identify periods of expanding or contracting volatility
- Set dynamic stop-loss levels based on current market conditions
- Detect volatility squeezes that precede large moves
- Size positions appropriately for current market risk

Works best on daily and intraday charts for liquid instruments. Shorter parameter values suit scalping and day trading while longer values work for swing and position trading.

## Risk Management

No indicator is predictive on its own. Always define risk before entering a trade:

- Set stop-losses based on ATR or recent swing points, not arbitrary percentages
- Size positions so that a stop-loss hit risks no more than 1-2% of account equity
- Avoid adding to losing positions based solely on indicator readings
- Backtest parameter combinations on out-of-sample data before live trading

## Combining with Other Indicators

- **Moving Average Ribbon**: Use the Moving Average Ribbon to confirm the overall trend direction before acting on this indicator's signals. Trading in the direction of the ribbon produces higher win rates.
- **Volume Profile POC**: When this indicator's signal aligns with a high-volume node from the Volume Profile, the confluence creates a stronger setup with better follow-through.
- **RSI or Stochastic**: Add a momentum oscillator as a confirmation filter. Signals that align with oversold or overbought momentum readings tend to produce larger moves.
