# EMA Crossover

The EMA Crossover strategy is one of the most widely used trend-following systems in technical analysis. It generates buy signals when a fast exponential moving average crosses above a slow EMA, and sell signals on the opposite crossover. This implementation adds a long-term trend filter EMA (default 100 periods) that restricts long entries to uptrending markets, preventing the strategy from buying dips in a bear trend. The result is a filtered, long-only crossover system built for riding sustained momentum moves.

## Conceptual Diagram

![Concept](concept.svg)


## How It Works

The strategy computes three exponential moving averages. The fast EMA (default 9) responds quickly to price changes and captures short-term momentum. The slow EMA (default 21) smooths out noise and represents the intermediate trend. The trend EMA (default 100) serves as a directional filter, only permitting trades in the direction of the long-term trend.

A long entry requires two conditions: the fast EMA must cross above the slow EMA (bullish crossover), AND the current close must be above the trend EMA. The crossover indicates that short-term momentum has shifted bullish, while the trend filter confirms that this momentum aligns with the broader market direction. Without the trend filter, the strategy would buy crossovers during bear markets, leading to repeated losses as rallies fail.

The exit condition is simpler: any fast-below-slow crossunder closes the long position regardless of the trend EMA. This asymmetry ensures quick exits when momentum fades, even if the long-term trend remains intact. The strategy will re-enter on the next bullish crossover as long as the trend filter still permits it.

The fill between the fast and slow EMAs on the chart provides a visual "ribbon" that shows the current momentum state. When the fast EMA is above (ribbon is positive), momentum favors longs. When below, the ribbon flips negative and the strategy is flat.

## Parameters

| Parameter | Default | Range | Description |
|-----------|---------|-------|-------------|
| Fast EMA Length | 9 | 2-50 | Period for the fast (responsive) exponential moving average |
| Slow EMA Length | 21 | 5-200 | Period for the slow (smoothed) exponential moving average |
| Trend Filter EMA | 100 | 20-500 | Long-term EMA used to filter entries to the prevailing trend direction |

## Python Advantage

The strategy computes three EMAs and evaluates compound entry conditions using clean array indexing and boolean logic.

```python
# Three EMAs computed as full numpy arrays in parallel
fast_ema = ta.ema(close, fast_len)
slow_ema = ta.ema(close, slow_len)
trend_ema = ta.ema(close, trend_len)

# Compound entry: crossover AND trend filter in one expression
long_cond = ta.crossover(fast_ema, slow_ema)[-1] and close[-1] > trend_ema[-1]
exit_cond = ta.crossunder(fast_ema, slow_ema)[-1]

# Visual ribbon fill between fast and slow EMAs
p1 = plot(fast_ema, title="Fast EMA", color="orange")
p2 = plot(slow_ema, title="Slow EMA", color="blue")
fill(p1, p2, color="rgba(0,150,255,0.1)")
```

The `ta.ema()` function computes the full EMA array for every bar in a single vectorized call. The `fill()` function creates a shaded region between two plot references, providing visual momentum feedback. The `[-1]` indexing accesses the current bar value from the full array without loops.

## When to Use

Works best on trending instruments across all timeframes, though daily and 4-hour charts offer the best signal quality. Effective on stocks with clear momentum phases, trending forex pairs, and index ETFs. The 9/21/100 default combination is a well-tested setup for daily swing trading. Reduce the trend filter length for shorter timeframes or increase it for position trading. Avoid on range-bound instruments where crossovers whipsaw frequently.

## Risk Management

The crossunder exit limits holding time during adverse moves, but it does not cap maximum drawdown. Add a fixed stop at 2-3 ATR below the entry price for tail risk protection. The trend filter is the primary risk control: it prevents the most dangerous trades (buying in a downtrend). Position size should be proportional to confidence in the trend: larger positions when all three EMAs are aligned and stacked (fast above slow above trend), smaller when the trend EMA is flat.

## Combining with Other Indicators

- **ADX Stochastic**: Use the Stochastic oscillator to time entries within the EMA crossover zone, buying pullbacks rather than chasing the crossover bar itself.
- **Choppiness Filter**: Add a choppiness check to avoid crossover signals during sideways markets where the strategy would whipsaw.
- **ATR Trailing Stop**: Replace the crossunder exit with an ATR trailing stop for better profit capture during strong trends where you do not want to exit on minor EMA recrosses.
