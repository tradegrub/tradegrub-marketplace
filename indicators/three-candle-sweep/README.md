# Three Candle Sweep

Three-candle price action pattern that identifies potential liquidity sweeps where the third candle reverses through the bodies of the two preceding candles. This price action indicator provides quantitative signals that can be applied to any liquid market across all timeframes.

## Conceptual Diagram

![Concept](concept.svg)

## How It Works

The indicator analyzes price data using price action techniques to produce actionable signals.

Core techniques include iterative computation, high-low range analysis. The computation processes all bars simultaneously using vectorized numpy operations, ensuring consistent results regardless of the dataset size.

Integer parameters control window lengths and thresholds, allowing the indicator to adapt from scalping on short timeframes to position trading on weekly charts. Shorter windows increase sensitivity to recent price action while longer windows provide smoother, more reliable signals.

## Parameters

| Parameter | Default | Range | Description |
|-----------|---------|-------|-------------|
| Cooldown Bars | 3 | 1 - 20 | Controls cooldown bars sensitivity (int) |

## Signals

- **Background shading**: Highlights active signal zones based on bull_bg
- **Background shading**: Highlights active signal zones based on bear_bg

## Python Advantage

The entire computation runs as vectorized numpy operations, processing all bars simultaneously rather than one at a time:

```python
hi = np.array(high, dtype=float)
lo = np.array(low, dtype=float)
n = len(cl)

bull_signal = np.zeros(n, dtype=bool)
bear_signal = np.zeros(n, dtype=bool)

last_bull = -999
last_bear = -999

for i in range(2, n):
```

Python's numpy arrays allow element-wise arithmetic across thousands of bars in a single expression. Adding custom variations or combining with other calculations is straightforward, requiring only standard array operations.

## When to Use

- Identify high-probability candlestick patterns automatically
- Confirm pattern signals with surrounding price context
- Filter patterns that form at key support and resistance levels
- Reduce subjective pattern interpretation with quantitative scoring

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
