# Pyramid Accumulator

Systematic accumulation strategy that builds a position by buying into price weakness and exits the entire position when a profit target is reached.

## How It Works

1. A simple moving average (SMA) defines the trend baseline
2. When price drops below the SMA and RSI falls below the oversold threshold, a buy order is placed
3. Multiple buy entries are allowed up to a configurable maximum (pyramid entries)
4. A cooldown period prevents entries from clustering too closely together
5. The strategy tracks average entry price across all pyramid entries
6. When price rises above the average entry by the target percentage, the entire position is closed

## Inputs

- **SMA Length**: Period for the reference moving average (default: 50)
- **RSI Length**: Period for the RSI filter (default: 14)
- **Oversold RSI Threshold**: RSI must be below this value to trigger a buy (default: 40)
- **Min Bars Between Buys**: Cooldown period between pyramid entries (default: 5)
- **Max Pyramid Entries**: Maximum number of buy entries allowed per position (default: 8)
- **Profit Target %**: Percentage above average entry price to trigger a full exit (default: 5.0)

## Usage Notes

- Works best on instruments that tend to mean-revert after dips
- Lower oversold thresholds produce fewer but higher-conviction entries
- Increasing max entries allows deeper accumulation but increases exposure
- The cooldown setting helps spread entries across a broader price decline rather than clustering at one level
