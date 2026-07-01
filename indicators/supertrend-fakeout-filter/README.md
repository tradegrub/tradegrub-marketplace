# Supertrend Fakeout Filter

Enhanced Supertrend that validates trend reversals by checking whether price moves far enough from the Supertrend line after a flip. If price fails to reach a minimum ATR-based distance within a configurable number of bars, the reversal is flagged as a fakeout.

## Conceptual Diagram

![Concept](concept.svg)

## Parameters

- **ATR Length** (1-50, default 10): Period for ATR calculation
- **Factor** (0.5-10, default 3.0): Supertrend multiplier
- **Fakeout Check Bars** (1-10, default 3): Bars after flip to verify distance
- **Min ATR Distance** (0.1-3.0, default 0.5): Minimum ATR multiples price must travel from Supertrend line

## Signals

- **Green triangle**: Confirmed bullish reversal (price moved far enough)
- **Red triangle**: Confirmed bearish reversal
- **Orange X**: Fakeout detected (price stayed too close after flip)

## Use Cases

- Reduce whipsaw losses on Supertrend entries
- Identify choppy conditions via fakeout frequency
- Combine with volume for higher-conviction trend signals
