# Multi-Oscillator Divergence

Scans for price-oscillator divergences simultaneously across RSI, MACD histogram, and Stochastic. Only signals when multiple oscillators agree on the divergence, producing higher-confidence reversal alerts than single-indicator divergence.

## Conceptual Diagram

![Concept](concept.svg)

## Parameters

- **RSI Length** (2-50, default 14): Period for RSI calculation
- **MACD Fast** (2-50, default 12): Fast EMA period
- **MACD Slow** (5-100, default 26): Slow EMA period
- **MACD Signal** (2-50, default 9): Signal line period
- **Divergence Lookback** (10-100, default 30): Window to search for prior swing extremes
- **Min Oscillators Agreeing** (1-3, default 2): Minimum number of oscillators confirming divergence

## Signals

- **Divergence Score**: Positive for bullish divergence, negative for bearish. Magnitude shows how many oscillators agree (1-3).
- **Triangle markers**: Appear when minimum agreement threshold is met
- Scores of +/-3 indicate all three oscillators confirm the divergence

## Use Cases

- Filter out weak single-oscillator divergences
- Identify high-probability reversal zones
- Combine with support/resistance for entry timing
