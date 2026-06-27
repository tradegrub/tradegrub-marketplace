# Moving Average Crossover

Buy when the fast SMA crosses above the slow SMA, sell when it crosses below.

## Parameters

| Name        | Default | Range    |
|-------------|---------|----------|
| Fast Period | 9       | 2 - 200  |
| Slow Period | 21      | 2 - 500  |

## How It Works

This strategy computes two simple moving averages with different lookback periods. A long entry is triggered when the fast MA crosses above the slow MA, indicating upward momentum. The position is closed when the fast MA crosses back below the slow MA.

## Signals

- **Long entry:** Fast SMA crosses above Slow SMA
- **Close:** Fast SMA crosses below Slow SMA

## Screenshot

_Coming soon_

## Install

Add this strategy from the TradeGrub marketplace or copy strategy.py into the script editor.
