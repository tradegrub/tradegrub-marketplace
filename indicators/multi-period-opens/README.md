# Multi Period Opens

Plots opening price levels for multiple timeframes on a single chart. These period opens serve as key reference points used by institutional traders for positioning and bias.

## Conceptual Diagram

![Concept](concept.svg)

## Levels

- **Daily Open**: Previous bar close (blue)
- **Weekly Open**: Close from ~5 bars ago (purple)
- **Monthly Open**: Close from ~21 bars ago (orange)
- **Yearly Open**: Close from ~252 bars ago (green)

## How to Use

Price trading above a period open suggests bullish bias for that timeframe. Price trading below suggests bearish bias. When multiple opens cluster together, that zone becomes a strong support or resistance area.

## Settings

- **Show Daily Open**: Toggle daily open level on/off
- **Show Weekly Open**: Toggle weekly open level on/off
- **Show Monthly Open**: Toggle monthly open level on/off
- **Show Yearly Open**: Toggle yearly open level on/off

## Notes

Period opens are approximated using fixed bar lookbacks on daily charts. Each level is labeled at the right edge of the chart for quick reference.
