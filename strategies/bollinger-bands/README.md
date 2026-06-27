# Bollinger Bands

Buy below the lower Bollinger Band and sell above the upper band for mean-reversion trades.

## Parameters

| Name              | Default | Range      |
|-------------------|---------|------------|
| Length            | 20      | 5 - 200    |
| Std Dev Multiplier| 2.0     | 0.5 - 5.0  |

## How It Works

This strategy calculates Bollinger Bands using a simple moving average and a standard deviation multiplier. A long entry triggers when price crosses above the lower band, suggesting an oversold bounce. The position closes when price crosses below the upper band.

## Signals

- **Long entry:** Close crosses above Lower Band
- **Close:** Close crosses below Upper Band

## Screenshot

_Coming soon_

## Install

Add this strategy from the TradeGrub marketplace or copy strategy.py into the script editor.
