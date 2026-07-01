# Renko Overlay

Overlays Renko-style bricks directly on the candlestick chart to filter out market noise and highlight the dominant trend direction. Renko charts ignore time and focus purely on price movement, forming a new brick only when price moves by a specified amount. This overlay brings that clarity to your standard time-based chart without losing the original candlestick context.

## Conceptual Diagram

![Concept](concept.svg)

## How It Works

Renko bricks are constructed using a fixed price increment called the "brick size." Starting from an initial reference price, the indicator monitors the close price on each bar:

1. **Brick Formation (Continuation):** If price moves in the current trend direction by at least one brick size, a new brick is added in that direction. Multiple bricks can form on a single bar if price moves far enough.

2. **Brick Formation (Reversal):** A reversal requires price to move against the current trend by at least two brick sizes. This built-in hysteresis reduces whipsaws and false signals.

3. **Brick Size Calculation:** The brick size can be set as a fixed value or calculated dynamically using ATR (Average True Range). ATR-based sizing adapts to current volatility, producing larger bricks in volatile markets and smaller bricks in quiet markets.

4. **Visual Output:** Each brick is drawn as a colored box on the chart. A midpoint trend line connects the center of each brick, providing a smooth trend reference.

## Parameters

| Parameter | Default | Range | Description |
|-----------|---------|-------|-------------|
| Brick Size Mode | ATR | ATR / Fixed | Whether to calculate brick size from ATR or use a fixed value |
| Fixed Brick Size | 1.0 | 0.01+ | The price increment per brick when using Fixed mode |
| ATR Length | 14 | 1 to 200 | Lookback period for ATR calculation |
| ATR Multiplier | 1.0 | 0.1 to 10.0 | Multiplier applied to the ATR value to set brick size |

## Signals

- **Green bricks:** Price is trending upward. Each green brick confirms a move of at least one brick size higher.
- **Red bricks:** Price is trending downward. Each red brick confirms a move of at least one brick size lower.
- **Reversal from green to red:** Bearish signal. Price has moved down by at least two brick sizes from the last up-brick top.
- **Reversal from red to green:** Bullish signal. Price has moved up by at least two brick sizes from the last down-brick bottom.
- **Yellow trend line:** The midpoint of the current brick, serving as a dynamic support/resistance reference.
- **Background tint:** A subtle green or red background shade indicates the current Renko trend direction at a glance.

## Python Advantage

The indicator uses numpy for efficient ATR and True Range calculations:

```python
tr_arr = np.maximum(
    high_arr - low_arr,
    np.maximum(
        np.abs(high_arr - np.roll(close_arr, 1)),
        np.abs(low_arr - np.roll(close_arr, 1))
    )
)
```

This vectorized approach computes True Range across all bars in a single operation, avoiding slow per-bar loops for the ATR component.

## When to Use

- **Trend identification:** Renko bricks clearly show when a trend is intact (consecutive same-color bricks) versus when it is reversing.
- **Noise reduction:** Ideal for choppy or sideways markets where candlestick patterns produce too many false signals.
- **Swing trading:** The two-brick reversal requirement naturally filters out minor pullbacks, keeping you in the trend longer.
- **Volatility adaptation:** ATR-based brick sizing automatically adjusts to changing market conditions, making the indicator effective across different instruments and timeframes.

## Risk Management

- **Trailing stops:** Place a stop loss at the opposite edge of the most recent brick. For a long position, trail your stop at the bottom of the last green brick.
- **Reversal exits:** Exit positions when the first brick of the opposite color forms, as this confirms a two-brick-size adverse move.
- **Position sizing:** Wider bricks (higher ATR or larger fixed size) imply wider stops. Reduce position size proportionally when brick size increases to maintain consistent risk per trade.
- **Breakout confirmation:** Use the Renko trend line as a filter. Only take breakout trades when the trend line agrees with the breakout direction.

## Combining With Other Indicators

- **Renko + Volume Profile:** Use volume profile to identify key support and resistance zones, then trade Renko reversals at those levels for higher-probability entries.
- **Renko + RSI:** When Renko bricks reverse to green while RSI is recovering from oversold territory (below 30), the confluence strengthens the bullish signal. The reverse applies for bearish reversals with overbought RSI.
- **Renko + Moving Averages:** Overlay a longer-period moving average and only take Renko signals in the direction of the moving average trend. This keeps you aligned with the higher timeframe direction.
