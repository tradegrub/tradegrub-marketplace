# Smart Money Concepts

> by tradegrub

Identifies order blocks, fair value gaps, and break-of-structure levels. Multi-timeframe analysis with alerts.

## Parameters

| Parameter | Default | Range |
|-----------|---------|-------|
| Swing Length | 5 | 2 - 20 |
| Show Order Blocks | True | - |
| Show Fair Value Gaps | True | - |
| Show Break of Structure | True | - |

## How It Works

Detects swing highs and lows over a configurable lookback window. When price closes beyond a previous swing level, a break-of-structure signal is plotted. Fair value gaps are highlighted when a candle gap leaves an imbalance between two non-adjacent bars.

## Signals

- **Buy:** Break of structure upward (close above previous swing high) or bullish fair value gap detected.
- **Sell:** Break of structure downward (close below previous swing low) or bearish fair value gap detected.

## Install

Add this from the TradeGrub marketplace or copy the script into the script editor.
