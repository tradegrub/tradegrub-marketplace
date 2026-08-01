# Logarithmic Moving Average

A weighted moving average where weights follow a logarithmic curve, giving progressively more weight to recent bars while maintaining smooth transitions. Includes a signal line for crossover detection.

## Conceptual Diagram

![Concept](concept.svg)

## Parameters

| Parameter | Type | Default | Range | Description |
|-----------|------|---------|-------|-------------|
| Length | int | 20 | 2-200 | LMA period |
| Signal Length | int | 9 | 2-50 | SMA period applied to LMA |

## Signals

- Triangle up: LMA crosses above signal line (bullish)
- Triangle down: LMA crosses below signal line (bearish)
- LMA above signal: uptrend bias
- LMA below signal: downtrend bias

## Usage

The logarithmic weighting gives more emphasis to recent prices than a simple moving average but less than an exponential moving average. Use the LMA/signal crossovers similarly to MACD line crossovers for trend-following entries.
