# Gap Fill Reversion

The Gap Fill Reversion strategy fades opening price gaps, betting that they will "fill" by reverting back to the prior session's close. Gaps occur when the opening price differs significantly from the previous close, often due to overnight news, earnings, or pre-market activity. Statistical studies show that a majority of gaps fill within a few bars, making this a well-documented mean-reversion edge. This implementation uses ATR-scaled gap detection, profit targets at the prior close, ATR stops, and a time-based exit to avoid holding stale positions.

## Conceptual Diagram

```
Price
 │
 │  ┌── Open (gap up)
 │  │   ╲                    Gap Up: SHORT
 │  │    ╲                   Target = prior close
 │  │     ╲  ╱╲
 │  │      ╲╱  ╲
 │  GAP     ╲───── Target (prior close)
 │  │
 │──┘ Prior Close
 │
 │──┐ Prior Close
 │  │
 │  GAP    ╱───── Target (prior close)
 │  │     ╱╲  ╱
 │  │    ╱  ╲╱
 │  │   ╱                    Gap Down: LONG
 │  └── Open (gap down)      Target = prior close
 │
 └──────────────────────────────── Time
      🔴 Fade gap up      🟢 Fade gap down
      (short)              (long)

   If not filled in 10 bars → close position
```

## How It Works

The strategy detects gaps by comparing the current bar's open to the previous bar's close. A gap-up exists when the open exceeds the prior close by more than a configurable multiple of ATR (default 0.5x). A gap-down exists when the prior close exceeds the current open by the same ATR-scaled threshold. Using ATR rather than a fixed point value makes the gap detection adaptive to the instrument's volatility.

When a gap-up is detected, the strategy enters short, expecting price to fall back toward the prior close. The profit target (limit order) is set at the prior close, and a stop-loss is placed above the open at an ATR multiple (default 1.5x). This creates a defined risk-reward trade where the reward is the gap size and the risk is a further extension beyond the open.

Gap-down detection triggers a long entry with the same structure: target at the prior close, stop below the open. The ATR-based stop ensures that risk is proportional to current volatility rather than a fixed amount.

The time-based exit is a critical safety feature. If the gap has not filled within the maximum bar count (default 10), the position is closed regardless of profit or loss. This prevents the strategy from holding a losing position indefinitely when the gap represents a genuine breakaway move rather than a fill candidate. The `ta.barsince()` function tracks the number of bars since the gap signal occurred.

## Parameters

| Parameter | Default | Range | Description |
|-----------|---------|-------|-------------|
| Min Gap Size (ATR mult) | 0.5 | 0.2-3.0 | Minimum gap size as a multiple of ATR to qualify as tradeable |
| ATR Length | 14 | 5-50 | Period for ATR calculation |
| ATR Stop Multiplier | 1.5 | 0.5-5.0 | Multiple of ATR for stop-loss distance beyond the open |
| Max Bars to Fill | 10 | 3-30 | Maximum number of bars to wait for gap fill before forcing exit |

## Python Advantage

The strategy uses numpy array arithmetic for gap detection, `ta.barsince()` for elapsed-time tracking, and the `strategy.exit()` function for simultaneous limit and stop order placement.

```python
# Gap detection using array indexing — prior close vs current open
gap_up = open[-1] - close[-2]
gap_down = close[-2] - open[-1]

# ATR-scaled gap qualification
is_gap_up = gap_up > atr[-2] * min_gap_atr
is_gap_down = gap_down > atr[-2] * min_gap_atr

# Simultaneous limit (target) and stop in one exit call
if is_gap_up:
    strategy.entry("Short Gap", strategy.SHORT)
    strategy.exit("Short Exit", "Short Gap",
                  limit=close[-2],        # Target: prior close (gap fill)
                  stop=open[-1] + atr[-1] * atr_stop)  # Stop: beyond open

# Time-based exit using bars-since tracking
bars_since_gap_up = ta.barsince(is_gap_up)
if bars_since_gap_up[-1] == max_bars:
    strategy.close("Short Gap")
```

The `strategy.exit()` with both `limit` and `stop` parameters creates a bracket order (OCO: one-cancels-other) from a single function call. The `ta.barsince()` function returns a numpy array tracking the bar count since the condition was last true, enabling time-based exits without manual counter management.

## When to Use

Best on liquid instruments that gap frequently: individual stocks at the open, index futures, and forex pairs during session transitions. The strategy is inherently an opening-bar strategy, so daily timeframes capture the overnight gap. Intraday timeframes (5-15 minute) can also be used to trade the first few bars after the gap. Avoid on instruments where gaps represent breakaway moves (e.g., biotech stocks on FDA announcements or earnings gaps on high-conviction results), as these gaps are less likely to fill.

## Risk Management

The ATR stop limits maximum loss per trade, and the time-based exit prevents indefinite exposure. The gap size threshold is the primary filter: larger minimums (1.0+ ATR) restrict trading to significant gaps that have stronger fill tendencies. Smaller gaps (0.2-0.5 ATR) trigger more trades but include many that are noise rather than genuine gap-fill opportunities. Always verify that the gap is not caused by a structural event (stock split, dividend, earnings) before fading it.

## Combining with Other Indicators

- **Bollinger Band Bounce**: Gaps that open beyond Bollinger Bands provide additional mean-reversion confluence for the fill trade.
- **EMA Distance**: Confirm that the gap has pushed price to an EMA distance extreme, adding statistical support to the reversion thesis.
- **Choppiness Filter**: Use the Choppiness Index to confirm the market is range-bound, avoiding gap fades during trending markets where gaps may represent continuation rather than reversal.
