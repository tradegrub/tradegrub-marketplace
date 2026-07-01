# Inside Bar Failure

Detects inside bar patterns and identifies breakout failures that often lead to strong reversals.

## Conceptual Diagram

![Concept](concept.svg)

## What It Does

An inside bar forms when a bar's high and low are completely contained within the previous bar's range. The previous bar is called the "mother bar."

After an inside bar, the indicator monitors subsequent bars for a breakout above or below the mother bar's range. If that breakout fails (price reverses and closes through the opposite side of the mother bar), a failure label appears on the chart.

Breakout failures are significant because they trap traders on the wrong side of the market and often produce strong moves in the reversal direction.

## Signals

- **Bull Fail**: Price broke above the mother bar high but then reversed and closed below the mother bar low. Bearish signal.
- **Bear Fail**: Price broke below the mother bar low but then reversed and closed above the mother bar high. Bullish signal.

## Inputs

- **Max Bars After Breakout**: How many bars after the initial breakout to watch for a failure (default 5)
- **Highlight Inside Bars**: Show a subtle background highlight on inside bars (default on)
- **Show Mother Bar Range**: Draw dotted lines at the mother bar high and low (default on)

## Usage

Works on any timeframe and any instrument. Higher timeframes (daily, weekly) tend to produce more reliable signals. Combine with volume or momentum indicators for confirmation.
