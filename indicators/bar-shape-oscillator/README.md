# Bar Shape Oscillator

An amplitude-free directional oscillator that uses only the shape of each candlestick bar, independent of price level or volatility.

## Conceptual Diagram

![Concept](concept.svg)

## How It Works

For each bar, computes:
- **Body ratio**: (close - open) / (high - low), signed to show direction
- **Close position**: (close - low) / (high - low), where the close sits in the range
- **Composite**: body_ratio * (2 * close_position - 1), combining direction with close strength

The composite is smoothed with an EMA to produce the oscillator (-1 to +1).

## Parameters

- **Smooth Length** (default 5): EMA smoothing period for the composite score

## Signals

- **Above 0.5**: Strong bullish bar shapes, buyers in control
- **Below -0.5**: Strong bearish bar shapes, sellers in control
- **Crossing zero**: Shift in bar character, potential trend change
- **Background**: Green tint for bullish, red tint for bearish extremes

## Usage

Use as a pure price-action momentum gauge that works across any timeframe or instrument without parameter tuning. Unlike RSI or MACD, it responds to the quality of each bar rather than magnitude. Useful for filtering entries in trending systems.
