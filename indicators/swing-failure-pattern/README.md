# Swing Failure Pattern

Detects Swing Failure Patterns (SFP) where price sweeps past a swing level then reverses back, signaling a liquidity grab and potential reversal.

## Conceptual Diagram

![Concept](concept.svg)

## Parameters

- **Pivot Length:** Number of bars on each side used to identify swing points (default: 5)
- **Lookback Period:** How many bars back to search for swing highs and lows (default: 50)

## Signals

- **Bearish SFP (red triangle above bar):** Price wicked above a recent swing high but closed back below it. This suggests sellers absorbed the breakout liquidity.
- **Bullish SFP (green triangle below bar):** Price wicked below a recent swing low but closed back above it. This suggests buyers absorbed the breakdown liquidity.

## How It Works

1. Swing highs and lows are identified using a pivot window (pivot length x 2 + 1 bars).
2. The most recent swing high and swing low levels within the lookback period are tracked.
3. On each bar, the indicator checks whether price swept above a swing high (or below a swing low) intrabar but closed on the opposite side.
4. When a sweep and reversal is confirmed, a signal shape is plotted and a horizontal line marks the swept level.
5. An oscillator plots +1 for bullish SFPs and -1 for bearish SFPs.
