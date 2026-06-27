# RSI Mean Reversion

Buy on RSI oversold crossover and sell on RSI overbought crossunder.

## Parameters

| Name            | Default | Range    |
|-----------------|---------|----------|
| RSI Length      | 14      | 2 - 100  |
| Oversold Level  | 30      | 5 - 50   |
| Overbought Level| 70      | 50 - 95  |

## How It Works

This strategy calculates the Relative Strength Index over a configurable period. A long entry triggers when RSI crosses above the oversold threshold, signaling a potential reversal from oversold conditions. The position closes when RSI crosses below the overbought threshold.

## Signals

- **Long entry:** RSI crosses above Oversold Level
- **Close:** RSI crosses below Overbought Level

## Screenshot

_Coming soon_

## Install

Add this strategy from the TradeGrub marketplace or copy strategy.py into the script editor.
