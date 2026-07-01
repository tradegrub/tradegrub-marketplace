# Consecutive Candle Streak

Tracks consecutive bullish and bearish candle streaks, then benchmarks them against historical averages to identify potential exhaustion and reversal points.

## Conceptual Diagram

![Concept](concept.svg)

## Parameters

- **Lookback Period:** Number of bars used to calculate average streak lengths (default: 200)
- **Exhaustion Multiplier x10:** Multiplier for the average streak length to define exhaustion threshold, scaled by 10 (default: 15, meaning 1.5x)

## Signals

- **Bull Exhaustion:** Orange triangle above bar when a bullish streak exceeds 1.5x the historical average bullish streak length
- **Bear Exhaustion:** Orange triangle below bar when a bearish streak exceeds 1.5x the historical average bearish streak length
- **Background highlight:** Light orange background appears during exhaustion signals

## How It Works

1. Each bar is classified as bullish (close > open) or bearish (close < open)
2. Consecutive same-direction bars are counted as a streak: positive values for bullish runs, negative for bearish
3. Over the lookback window, all completed streaks are collected and their average lengths computed separately for bullish and bearish
4. When the current streak length exceeds the average by the exhaustion multiplier, an exhaustion signal fires
5. The streak oscillator, bullish threshold, and bearish threshold are plotted as reference lines
