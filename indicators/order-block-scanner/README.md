# Order Block Scanner

![Concept](concept.svg)

The Order Block Scanner identifies candles where institutional accumulation or distribution likely occurred, based on the presence of a counter-trend candle immediately before a strong impulse move. These zones often act as future support or resistance when price returns.

## How It Works

- Scans for strong impulse candles exceeding a minimum ATR multiple
- Identifies the preceding counter-trend candle as the order block
- Bullish order blocks are bearish candles before strong bullish impulses
- Bearish order blocks are bullish candles before strong bearish impulses
- Draws boxes around order block zones and labels the most recent blocks

## Parameters

| Parameter | Default | Range | Description |
|-----------|---------|-------|-------------|
| Lookback | 10 | 3-50 | How far to extend order block boxes forward |
| Min Impulse | 1.5 | 0.5-5.0 | Minimum impulse size as ATR multiple |
| Max Active Blocks | 5 | 1-20 | Maximum number of blocks to display |
| Show Labels | true | - | Display order block text labels |

## Outputs

- **Bull OB Boxes**: Green shaded zones marking bullish order blocks
- **Bear OB Boxes**: Red shaded zones marking bearish order blocks
- **Markers**: Triangle markers at order block candles
- **Labels**: Text labels identifying block type

## Usage Notes

- Order blocks are most reliable on higher timeframes (1H, 4H, Daily)
- Look for price to return to an order block zone for potential entries
- Combine with break of structure or fair value gaps for stronger setups
