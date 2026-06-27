# Supertrend

Buy and sell on Supertrend direction flips using ATR-based trailing bands.

## Parameters

| Name       | Default | Range      |
|------------|---------|------------|
| ATR Length | 10      | 1 - 100    |
| Factor     | 3.0     | 0.5 - 10.0 |

## How It Works

This strategy uses the Supertrend indicator, which combines ATR with a multiplier to create dynamic support and resistance bands. A long entry triggers when the Supertrend direction flips bullish. The position closes when the direction flips bearish.

## Signals

- **Long entry:** Supertrend direction flips bullish (crosses above 0)
- **Close:** Supertrend direction flips bearish (crosses below 0)

## Screenshot

_Coming soon_

## Install

Add this strategy from the TradeGrub marketplace or copy strategy.py into the script editor.
