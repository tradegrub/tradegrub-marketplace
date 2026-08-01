# Pyramid Accumulator
from tg_scripting import *
import numpy as np

indicator("Pyramid Accumulator", overlay=True)

sma_len = input.int(50, "SMA Length", minval=10, maxval=200)
rsi_len = input.int(14, "RSI Length", minval=5, maxval=30)
oversold = input.int(40, "Oversold RSI Threshold", minval=10, maxval=50)
cooldown = input.int(5, "Min Bars Between Buys", minval=1, maxval=50)
max_entries = input.int(8, "Max Pyramid Entries", minval=1, maxval=20)
target_pct = input.float(5.0, "Profit Target %", minval=0.5, maxval=50.0)

sma = ta.sma(close, sma_len)
rsi = ta.rsi(close, rsi_len)

plot(sma, title="SMA", color="#42a5f5", linewidth=2)

n = len(close)
close_arr = np.array(close, dtype=float)
sma_arr = np.array(sma, dtype=float)
rsi_arr = np.array(rsi, dtype=float)

# Track pyramid state
position_count = 0
total_cost = 0.0
avg_entry = 0.0
last_buy_bar = -cooldown - 1

for i in range(sma_len, n):
    strategy.set_bar_index(i)
    price = close_arr[i]

    # Exit: sell entire position when profit target is hit
    if position_count > 0 and price >= avg_entry * (1.0 + target_pct / 100.0):
        pct_gain = (price / avg_entry - 1.0) * 100.0
        strategy.close("Pyramid")
        label.new(x=i, y=float(high[i]), text=f"EXIT ALL\n{position_count} lots\n+{pct_gain:.1f}%",
                  style=label.style_label_down, color="#00e676",
                  textcolor="#000000", size="small")
        position_count = 0
        total_cost = 0.0
        avg_entry = 0.0
        last_buy_bar = i
        continue

    # Entry: accumulate when price < SMA and RSI < oversold, respecting cooldown
    if (position_count < max_entries
            and (i - last_buy_bar) >= cooldown
            and not np.isnan(sma_arr[i])
            and not np.isnan(rsi_arr[i])
            and price < sma_arr[i]
            and rsi_arr[i] < oversold):
        strategy.entry("Pyramid", strategy.LONG)
        position_count += 1
        total_cost += price
        avg_entry = total_cost / position_count
        last_buy_bar = i
        label.new(x=i, y=float(low[i]), text=f"BUY #{position_count}",
                  style=label.style_label_up, color="#ff9800",
                  textcolor="#000000", size="tiny")
