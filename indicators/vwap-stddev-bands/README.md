# VWAP StdDev Bands

> by vkumar

Volume-weighted average price with configurable standard deviation bands. Automatically resets at session open for intraday timeframes.

## Parameters

| Parameter | Default | Range |
|-----------|---------|-------|
| Length | 14 | 1 - 200 |
| StdDev Multiplier | 2.0 | 0.5 - 5.0 |

## How It Works

Calculates the volume-weighted average price and plots standard deviation bands around it. The bands widen during volatile periods and contract during consolidation. Useful for identifying overbought and oversold conditions relative to VWAP.

## Signals

- **Buy:** Price touches or crosses below the lower band, indicating a potential mean-reversion long entry.
- **Sell:** Price touches or crosses above the upper band, indicating a potential mean-reversion short entry or exit.

## Install

Add this from the TradeGrub marketplace or copy the script into the script editor.
