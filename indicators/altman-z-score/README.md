# Altman Z-Score

Altman's five-factor bankruptcy prediction score with the distress, grey and safe zones marked on the pane.

## Conceptual Diagram

![Concept](concept.svg)

## Parameters

| Parameter | Default | Range | Description |
|-----------|---------|-------|-------------|
| Reporting period | FY | FY or FQ | Annual or quarterly statements used for the five ratios |

## Signals

- Z above 2.99: safe zone, bankruptcy within two years historically unlikely
- Z between 1.81 and 2.99: grey zone, the model gives no clear verdict
- Z below 1.81: distress zone, elevated historical bankruptcy risk
- A falling Z-score across consecutive filings is more informative than any single reading

## Usage

Use as a solvency screen before taking a long position in a leveraged or cyclical business, and as a risk overlay on any value setup. The market value term means the score moves with price between filings, unlike a purely statement-based score.

## Data Requirements

This script reads filed financial statements through `request.financial()`, so it
needs fundamental data for the charted symbol. On instruments without filed
statements, such as crypto pairs, forex and most indices, the series is empty and
nothing plots. Values step only at each filing date and stay flat in between.
