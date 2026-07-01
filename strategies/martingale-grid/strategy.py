# Martingale Grid Strategy
from tg_scripting import *
import numpy as np

indicator("Martingale Grid", overlay=True)

grid_depth = input.float(1.5, "Grid Depth %", minval=0.5, maxval=5.0)
multiplier = input.float(1.5, "Martingale Multiplier", minval=1.0, maxval=4.0)
max_orders = input.int(6, "Max Grid Orders", minval=2, maxval=12)
tp_pct = input.float(2.0, "Take Profit %", minval=0.5, maxval=10.0)
sl_pct = input.float(10.0, "Stop Loss %", minval=2.0, maxval=30.0)
sma_len = input.int(50, "SMA Length", minval=10, maxval=200)
show_labels = input.bool(True, "Show Labels")
show_levels = input.bool(True, "Show TP/SL Levels")

sma = ta.sma(close, sma_len)
plot(sma, title="SMA", color="blue")

# Entry trigger: price crosses under SMA (pullback entry)
entry_signal = ta.crossunder(close, sma)

n = len(close)

# Track grid state
in_grid = False
first_entry_price = 0.0
grid_orders_filled = 0
total_cost = 0.0
total_qty = 0.0
avg_entry = 0.0
tp_price = 0.0
sl_price = 0.0
level_start_bar = 0

for i in range(1, n):
    if in_grid:
        current_price = float(close[i])

        # Check for take profit
        if current_price >= tp_price:
            strategy.close("Grid Long")
            if show_labels:
                label.new(x=i, y=float(high[i]), text="TP HIT",
                          style=label.style_label_down, color="#00e676",
                          textcolor="#000000", size="tiny")
            in_grid = False
            continue

        # Check for stop loss
        if current_price <= sl_price:
            strategy.close("Grid Long")
            if show_labels:
                label.new(x=i, y=float(low[i]), text="SL HIT",
                          style=label.style_label_up, color="#ef5350",
                          textcolor="#ffffff", size="tiny")
            in_grid = False
            continue

        # Check if next grid level is hit
        if grid_orders_filled < max_orders:
            next_level = first_entry_price * (1.0 - grid_depth / 100.0 * grid_orders_filled)
            if current_price <= next_level:
                order_size = multiplier ** (grid_orders_filled - 1)
                order_cost = current_price * order_size
                total_cost += order_cost
                total_qty += order_size
                avg_entry = total_cost / total_qty
                grid_orders_filled += 1

                # Recalculate TP from new average entry
                tp_price = avg_entry * (1.0 + tp_pct / 100.0)

                strategy.entry("Grid Long", strategy.LONG)

                if show_labels:
                    label.new(x=i, y=float(low[i]),
                              text="G" + str(grid_orders_filled),
                              style=label.style_label_up, color="#ff9800",
                              textcolor="#000000", size="tiny")

                # Update TP line
                if show_levels:
                    end_bar = min(i + 40, n - 1)
                    line.new(x1=i, y1=tp_price, x2=end_bar, y2=tp_price,
                             color="#00e676", width=1, style=line.style_dashed)

    # New grid entry on SMA crossunder (only when not already in a grid)
    if not in_grid and entry_signal[i]:
        first_entry_price = float(close[i])
        order_size = 1.0
        total_cost = first_entry_price * order_size
        total_qty = order_size
        avg_entry = first_entry_price
        grid_orders_filled = 1
        in_grid = True
        level_start_bar = i

        tp_price = avg_entry * (1.0 + tp_pct / 100.0)
        sl_price = first_entry_price * (1.0 - sl_pct / 100.0)

        strategy.entry("Grid Long", strategy.LONG)

        if show_labels:
            label.new(x=i, y=float(low[i]), text="G1\nENTRY",
                      style=label.style_label_up, color="#42a5f5",
                      textcolor="#ffffff", size="tiny")

        if show_levels:
            end_bar = min(i + 60, n - 1)
            # TP level
            line.new(x1=i, y1=tp_price, x2=end_bar, y2=tp_price,
                     color="#00e676", width=1, style=line.style_dashed)
            label.new(x=i + 2, y=tp_price, text="TP",
                      style=label.style_label_left, color="rgba(0,230,118,0.2)",
                      textcolor="#00e676", size="small")
            # SL level
            line.new(x1=i, y1=sl_price, x2=end_bar, y2=sl_price,
                     color="#ef5350", width=1, style=line.style_dashed)
            label.new(x=i + 2, y=sl_price, text="SL",
                      style=label.style_label_left, color="rgba(239,83,80,0.2)",
                      textcolor="#ef5350", size="small")

            # Draw grid levels
            for g in range(1, max_orders):
                grid_price = first_entry_price * (1.0 - grid_depth / 100.0 * g)
                if grid_price > sl_price:
                    line.new(x1=i, y1=grid_price, x2=end_bar, y2=grid_price,
                             color="#ff9800", width=1, style=line.style_dotted)
                    label.new(x=i + 2, y=grid_price, text="G" + str(g + 1),
                              style=label.style_label_left,
                              color="rgba(255,152,0,0.2)",
                              textcolor="#ff9800", size="tiny")
