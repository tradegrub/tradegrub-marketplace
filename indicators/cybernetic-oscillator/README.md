# Cybernetic Oscillator

Bandpass filter oscillator using cascaded highpass and lowpass EMA filtering to isolate a target frequency band from price action. This oscillator indicator provides quantitative signals that can be applied to any liquid market across all timeframes.

## Conceptual Diagram

![Concept](concept.svg)

## How It Works

The indicator analyzes price data using oscillator techniques to produce actionable signals.

Built-in technical functions used: `ema`. These provide the foundation for the indicator's calculations, computed efficiently across the full price history in a single pass.

Core techniques include exponential moving average, simple moving average, iterative computation, extremum detection. The computation processes all bars simultaneously using vectorized numpy operations, ensuring consistent results regardless of the dataset size.

Integer parameters control window lengths and thresholds, allowing the indicator to adapt from scalping on short timeframes to position trading on weekly charts. Shorter windows increase sensitivity to recent price action while longer windows provide smoother, more reliable signals.

## Parameters

| Parameter | Default | Range | Description |
|-----------|---------|-------|-------------|
| Highpass Length | 10 | 2 - 50 | Controls highpass length sensitivity (int) |
| Lowpass Length | 20 | 5 - 100 | Controls lowpass length sensitivity (int) |

## Signals

- **Bandpass**: Primary visual output plotted as a continuous line on the chart
- **Trigger**: Primary visual output plotted as a continuous line on the chart
- **Bull Signal**: Discrete signal marker displayed at key points
- **Bear Signal**: Discrete signal marker displayed at key points
- **Zero** (0): Reference level for threshold-based decisions
- **Upper** (60): Reference level for threshold-based decisions
- **Lower** (-60): Reference level for threshold-based decisions
- **Background shading**: Highlights active signal zones based on cross_up.tolist()
- **Background shading**: Highlights active signal zones based on cross_down.tolist()

## Python Advantage

The entire computation runs as vectorized numpy operations, processing all bars simultaneously rather than one at a time:

```python
cl = np.array(close, dtype=float)
n = len(cl)

hp_ema = np.array(ta.ema(close, hp_length), dtype=float)
hp_ema = np.nan_to_num(hp_ema, nan=cl[0] if n > 0 else 0.0)
highpass = cl - hp_ema

lp_alpha = 2.0 / (lp_length + 1)
bandpass = np.zeros(n)
bandpass[0] = highpass[0]
for i in range(1, n):
```

Python's numpy arrays allow element-wise arithmetic across thousands of bars in a single expression. Adding custom variations or combining with other calculations is straightforward, requiring only standard array operations.

## When to Use

- Identify overbought and oversold conditions for mean reversion
- Detect divergences between price and the oscillator
- Time entries at extreme readings with confirmation
- Monitor zero-line crossovers for directional bias changes

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
