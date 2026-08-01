# Candlestick Pattern Score

Composite candlestick pattern recognition indicator that weights each detected pattern by its historical success rate over a rolling lookback window.

## Conceptual Diagram

![Concept](concept.svg)

## Detected Patterns

- Hammer / Inverted Hammer
- Doji
- Bullish / Bearish Engulfing
- Bullish / Bearish Harami
- Morning Star / Evening Star

## Parameters

- **Lookback:** Rolling window for calculating pattern hit rates (default 200, range 50 to 500)

## Signals

- **Positive score:** Net bullish pattern activity weighted by success rate
- **Negative score:** Net bearish pattern activity weighted by success rate
- **Above +50:** Strong bullish zone (green background highlight)
- **Below -50:** Strong bearish zone (red background highlight)
- **Zero line:** Neutral baseline

## Usage

Apply to any timeframe. Longer lookback periods produce more stable hit rate estimates but adapt more slowly. Shorter lookbacks react faster to regime changes but may have noisier success rate calculations.

Combine with trend or volume indicators for confirmation. The score reflects both pattern presence and historical reliability, so a high score means multiple reliable bullish patterns are firing simultaneously.
