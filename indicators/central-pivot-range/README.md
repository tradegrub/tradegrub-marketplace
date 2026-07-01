# Central Pivot Range

Plots the Central Pivot Range (CPR) on a price chart with Pivot, Top Central (TC), and Bottom Central (BC) levels. Highlights narrow CPR zones that often precede breakout moves.

## Conceptual Diagram

![Concept](concept.svg)

## Parameters

- **Lookback Period** (default 20): Number of bars used to calculate the previous high, low, and close for pivot computation.
- **Narrow CPR Threshold %** (default 50): Percentage of the average CPR width. When the current CPR width falls below this threshold, a background highlight signals a potential breakout.

## Signals

- **Narrow CPR highlight**: Orange-tinted background appears when the CPR width is unusually tight relative to its recent average. A contracting range suggests price compression and a potential breakout.
- **TC/BC zone**: The shaded area between TC and BC marks the central pivot range. Price staying above TC is bullish; below BC is bearish. Price inside the zone is neutral/consolidating.

## How It Works

1. Previous high, low, and close are derived from a rolling lookback window.
2. Pivot = (Previous High + Previous Low + Previous Close) / 3
3. BC (Bottom Central) = (Previous High + Previous Low) / 2
4. TC (Top Central) = 2 * Pivot - BC
5. CPR Width is measured as a percentage of price, then compared against its rolling average to detect narrow (developing) CPR conditions.
