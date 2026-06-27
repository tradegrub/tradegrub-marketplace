# Volume Profile POC

> by mike_l

Horizontal volume profile with Point of Control, Value Area High/Low. Configurable lookback and row count.

## Parameters

| Parameter | Default | Range |
|-----------|---------|-------|
| Lookback Bars | 100 | 10 - 500 |
| Row Count | 24 | 10 - 100 |
| Value Area % | 70.0 | 50.0 - 90.0 |

## How It Works

Divides the price range over the lookback period into equal-sized rows and accumulates volume into each row. The row with the highest volume is the Point of Control (POC). The Value Area is expanded outward from the POC until the configured percentage of total volume is captured, defining VAH and VAL levels.

## Signals

- **Buy:** Price approaches or bounces off the VAL or POC from below, suggesting institutional support.
- **Sell:** Price approaches or rejects from the VAH or POC from above, suggesting institutional resistance.

## Install

Add this from the TradeGrub marketplace or copy the script into the script editor.
