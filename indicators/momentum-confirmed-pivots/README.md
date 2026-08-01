# Momentum Confirmed Pivots

Identifies swing highs and lows that are confirmed by momentum alignment. Pivot highs require overbought momentum (RSI above threshold) and pivot lows require oversold momentum (RSI below threshold), filtering out pivots that lack conviction.

## Conceptual Diagram

![Concept](concept.svg)

## Parameters

- **Pivot Lookback** (3-50, default 10): Bars each side to confirm a swing point
- **RSI Length** (2-50, default 14): Period for RSI momentum calculation
- **RSI Confirmation Level** (20-80, default 50): RSI must exceed this for pivot highs, or fall below its inverse for pivot lows
- **Extend Pivot Levels** (default on): Draw dotted horizontal lines from confirmed pivots

## Signals

- **PH label**: Momentum-confirmed pivot high with optional resistance extension
- **PL label**: Momentum-confirmed pivot low with optional support extension
- Unconfirmed pivots are hidden, reducing chart noise

## Use Cases

- Identify high-conviction support and resistance levels
- Filter out weak swing points in choppy markets
- Combine with trend indicators for confluence-based entries
