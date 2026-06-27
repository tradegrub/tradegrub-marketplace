# SuperTrend Pro

> by aravind_r

Enhanced SuperTrend with ATR multiplier, trailing stop visualization, and buy/sell signal markers. Optimized for crypto volatility.

## Parameters

| Parameter | Default | Range |
|-----------|---------|-------|
| ATR Period | 10 | 1 - 100 |
| Multiplier | 3.0 | 0.5 - 10.0 |
| Trailing Stop | True | - |

## How It Works

Calculates the SuperTrend indicator using ATR to determine trend direction. When the direction flips positive, a long entry is triggered; when it flips negative, a short entry is triggered. An optional trailing stop uses the ATR multiplied by the configured factor to lock in profits.

## Signals

- **Buy:** SuperTrend direction crosses above zero (trend turns bullish).
- **Sell:** SuperTrend direction crosses below zero (trend turns bearish).

## Install

Add this from the TradeGrub marketplace or copy the script into the script editor.
