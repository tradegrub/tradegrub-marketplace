# Markov Regime Oscillator

Simple two-state Markov chain that classifies each bar as "trending" (absolute return exceeds the rolling median) or "ranging". Counts transition probabilities within a rolling window to estimate persistence of each regime. High P(Trend Persists) suggests momentum strategies will work; high P(Range Persists) favors mean-reversion.

## Conceptual Diagram

![Concept](concept.svg)

## Parameters

| Parameter | Default | Range | Description |
|-----------|---------|-------|-------------|
| Lookback | 50 | 20-200 | Rolling window for transition counting |

## Signals

- P(Trend Persists) above 60%: trending regime is sticky, use momentum strategies
- P(Range Persists) above 60%: ranging regime is sticky, use mean-reversion strategies
- Trend Probability above 50%: currently in a trending regime
- Crossovers between persistence lines: regime transition underway

## Usage

Use as a regime classifier to switch between trend-following and mean-reversion strategies. When both persistence probabilities are near 50%, the market is in transition and strategy selection is uncertain. Works best on daily and higher timeframes.
