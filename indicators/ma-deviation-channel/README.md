# MA Deviation Channel

Dynamic price channels constructed from historical percentage deviation statistics around a moving average.

## Conceptual Diagram

![Concept](concept.svg)

## How It Works

1. A moving average (SMA or EMA) is calculated as the center line.
2. For each bar, the percentage deviation from the MA is computed: `(close - MA) / MA * 100`.
3. Over a rolling lookback window, the indicator calculates:
   - **Average High Deviation**: mean of all positive deviations
   - **Average Low Deviation**: mean of all negative deviations
   - **Extreme High Deviation**: 95th percentile of deviations
   - **Extreme Low Deviation**: 5th percentile of deviations
4. These deviation percentages are applied back to the MA to form channel lines.

## Why This Is Different

Standard envelope indicators use a fixed percentage offset, which ignores changing volatility. Standard deviation bands assume a normal distribution. This indicator uses actual historical deviation behavior, so the channels adapt to how price has really moved around the average, including asymmetric moves.

## Inputs

- **MA Length** (default 50): period for the center moving average
- **MA Type** (default SMA): choose SMA (1) or EMA (2)
- **Deviation Lookback** (default 100): number of bars used to calculate deviation statistics
- **Show Extreme Bands** (default true): toggle the 95th/5th percentile extreme bands

## Interpretation

- Price reaching the average upper band suggests typical overbought conditions.
- Price reaching the extreme upper band suggests historically unusual extension.
- The same logic applies in reverse for the lower bands.
- Narrowing channels indicate reduced volatility; widening channels indicate increased volatility.
