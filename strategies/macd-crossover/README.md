# MACD Crossover

Buy when the MACD line crosses above the signal line, sell on the cross below.

## Parameters

| Name          | Default | Range    |
|---------------|---------|----------|
| Fast Length   | 12      | 2 - 100  |
| Slow Length   | 26      | 2 - 200  |
| Signal Length | 9       | 2 - 50   |

## How It Works

This strategy computes the MACD line (difference between fast and slow EMAs) and a signal line (EMA of the MACD). A long entry triggers when the MACD line crosses above the signal line, indicating bullish momentum. The position closes on the bearish crossunder.

## Signals

- **Long entry:** MACD line crosses above Signal line
- **Close:** MACD line crosses below Signal line

## Screenshot

_Coming soon_

## Install

Add this strategy from the TradeGrub marketplace or copy strategy.py into the script editor.
