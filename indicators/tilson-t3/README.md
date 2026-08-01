# Tilson T3 Moving Average

Six-stage ultra-smooth moving average designed by Tim Tilson. Reduces lag while maintaining smoothness through a cascaded EMA approach with configurable volume factor.

## Conceptual Diagram

![Concept](concept.svg)

## Parameters

- **Length** (default 20): Base EMA period for all six stages
- **Volume Factor** (default 0.7): Controls responsiveness vs smoothness. Higher values make T3 more responsive but less smooth.

## How It Works

T3 chains six EMAs together and combines the last four using polynomial coefficients derived from the volume factor:

- e1 through e6 are successive EMAs of each other
- T3 = c1*e6 + c2*e5 + c3*e4 + c4*e3

A 5-period SMA signal line is plotted alongside for crossover signals.

## Signals

- **T3 above Signal**: Bullish momentum
- **T3 below Signal**: Bearish momentum
- **T3/Signal crossover**: Potential entry or exit point
- **T3 slope direction**: Indicates trend acceleration or deceleration

## Usage

Use as a trend-following overlay. The T3 is significantly smoother than a standard EMA of the same length, making it effective for identifying the underlying trend without excessive whipsaws. Adjust the volume factor to tune responsiveness.
