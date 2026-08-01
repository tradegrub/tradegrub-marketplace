# Quasimodo Reversal

Detects Quasimodo (QML) reversal patterns using zigzag swing analysis. A Quasimodo forms when price makes a higher high followed by a lower low (bullish) or a lower low followed by a higher high (bearish), breaking the expected swing symmetry and signaling a potential reversal.

## Conceptual Diagram

![Concept](concept.svg)

## Parameters

- **Zigzag Threshold %** (0.5-15, default 3.0): Minimum percentage move to confirm a swing pivot
- **Draw Pattern Lines** (default on): Connect swing highs and lows with dotted lines

## Signals

- **Green QML label**: Bullish Quasimodo at lower low after higher high sequence
- **Red QML label**: Bearish Quasimodo at higher high after lower low sequence
- **Dotted lines**: Connect the swing points forming the pattern

## Use Cases

- Identify high-probability reversal zones at market turning points
- Combine with supply/demand zones for confluence entries
- Use zigzag threshold to match the timeframe volatility
