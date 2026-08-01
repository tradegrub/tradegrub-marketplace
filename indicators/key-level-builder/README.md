# Key Level Builder

Automatic key support and resistance level detection using scipy peak finding and numpy density-based clustering. This support and resistance indicator provides quantitative signals that can be applied to any liquid market across all timeframes.

## Conceptual Diagram

![Concept](concept.svg)

## How It Works

The indicator analyzes price data using support and resistance techniques to produce actionable signals.

Built-in technical functions used: `atr`. These provide the foundation for the indicator's calculations, computed efficiently across the full price history in a single pass.

Core techniques include exponential moving average, simple moving average, ATR, mean computation. The computation processes all bars simultaneously using vectorized numpy operations, ensuring consistent results regardless of the dataset size.

Integer parameters control window lengths and thresholds, allowing the indicator to adapt from scalping on short timeframes to position trading on weekly charts. Shorter windows increase sensitivity to recent price action while longer windows provide smoother, more reliable signals.

Float parameters fine-tune sensitivity and scaling factors. Small adjustments to these values can significantly change signal frequency and quality, so test changes on historical data before applying to live trading.

## Parameters

| Parameter | Default | Range | Description |
|-----------|---------|-------|-------------|
| Pivot Order | 10 | 3 - 30 | Controls pivot order sensitivity (int) |
| Number of Levels | 5 | 2 - 10 | Controls number of levels sensitivity (int) |
| Zone Width (ATR | 0.5 |  | Controls zone width (atr sensitivity (float) |

## Signals

- **Close**: Primary visual output plotted as a continuous line on the chart

## Python Advantage

The entire computation runs as vectorized numpy operations, processing all bars simultaneously rather than one at a time:

```python
n = len(cl)

atr_arr = np.array(ta.atr(high, low, close, 14), dtype=float)
atr_arr = np.nan_to_num(atr_arr, nan=1.0)
avg_atr = float(np.mean(atr_arr[14:]))

peak_idx = argrelextrema(hi, np.greater_equal, order=order)[0]
trough_idx = argrelextrema(lo, np.less_equal, order=order)[0]

pivots = []
for i in peak_idx:
```

Python's numpy arrays allow element-wise arithmetic across thousands of bars in a single expression. Adding custom variations or combining with other calculations is straightforward, requiring only standard array operations.

## When to Use

- Identify key price levels where reversals are likely
- Set profit targets at the next resistance or support level
- Detect breakouts above resistance or breakdowns below support
- Plan entries near support with tight stop-losses below

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
