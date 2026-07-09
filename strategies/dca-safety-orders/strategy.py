# Safety Order DCA Strategy
from tg_scripting import *
import numpy as np

strategy("Safety Order DCA", overlay=True)

# --- Inputs ---
initial_drop = input.float(1.0, "Initial Drop %", minval=0.1, maxval=10.0)
safety_step = input.float(1.5, "Safety Order Step %", minval=0.5, maxval=10.0)
step_scale = input.float(1.5, "Step Scale", minval=1.0, maxval=5.0)
volume_scale = input.float(1.5, "Volume Scale", minval=1.0, maxval=5.0)
target_profit = input.float(2.0, "Target Profit %", minval=0.5, maxval=20.0)
max_orders = input.int(5, "Max Safety Orders", minval=1, maxval=15)
sma_len = input.int(50, "SMA Length", minval=5, maxval=200)
show_labels = input.bool(True, "Show Labels")
show_levels = input.bool(True, "Show Safety Order Levels")

# --- Core indicators ---
sma_val = ta.sma(close, sma_len)
plot(sma_val, title="SMA", color="#42a5f5", linewidth=1)

n = len(close)
base_size = 1.0

# --- State tracking ---
in_deal = False
entry_bar = 0
avg_entry = 0.0
total_qty = 0.0
total_cost = 0.0
filled_orders = 0

for i in range(sma_len, n):
    price = float(close[i])

    if not in_deal:
        # Entry condition: price crosses below SMA
        if close[i] < sma_val[i] and close[i - 1] >= sma_val[i - 1]:
            in_deal = True
            entry_bar = i
            qty = base_size
            total_qty = qty
            total_cost = price * qty
            avg_entry = price
            filled_orders = 0

            strategy.entry("DCA Base", strategy.LONG)

            if show_labels:
                label.new(x=i, y=float(low[i]), text="BASE\nBUY",
                          style=label.style_label_up, color="#00e676",
                          textcolor="#000000", size="normal")

            # Draw safety order levels
            if show_levels:
                cumulative_drop = initial_drop
                for order_num in range(1, max_orders + 1):
                    so_price = price * (1.0 - cumulative_drop / 100.0)
                    end_bar = min(i + 60, n - 1)
                    line.new(x1=i, y1=so_price, x2=end_bar, y2=so_price,
                             color="#ff9800", width=1, style=line.style_dotted)
                    label.new(x=i + 2, y=so_price,
                              text=f"SO {order_num}",
                              style=label.style_label_left,
                              color="rgba(255,152,0,0.2)",
                              textcolor="#ff9800", size="tiny")
                    cumulative_drop += safety_step * (step_scale ** (order_num - 1))
    else:
        # Check safety order fills
        if filled_orders < max_orders:
            cumulative_drop = initial_drop
            for order_num in range(1, filled_orders + 2):
                if order_num <= filled_orders:
                    cumulative_drop += safety_step * (step_scale ** (order_num - 1))
                    continue
                so_price = float(close[entry_bar]) * (1.0 - cumulative_drop / 100.0)
                if price <= so_price:
                    qty = base_size * (volume_scale ** order_num)
                    total_qty += qty
                    total_cost += price * qty
                    avg_entry = total_cost / total_qty
                    filled_orders = order_num

                    strategy.entry("DCA SO " + str(order_num), strategy.LONG)

                    if show_labels:
                        label.new(x=i, y=float(low[i]),
                                  text=f"SO {order_num}\n{qty:.1f}x",
                                  style=label.style_label_up, color="#ff9800",
                                  textcolor="#000000", size="small")
                break

        # Check take profit
        tp_price = avg_entry * (1.0 + target_profit / 100.0)
        if price >= tp_price:
            strategy.close_all()
            in_deal = False

            if show_labels:
                label.new(x=i, y=float(high[i]),
                          text=f"TP\n+{target_profit}%",
                          style=label.style_label_down, color="#00e676",
                          textcolor="#000000", size="normal")

            # Draw avg entry and TP hit
            if show_levels:
                line.new(x1=entry_bar, y1=avg_entry, x2=i, y2=avg_entry,
                         color="#42a5f5", width=1, style=line.style_dashed)
                label.new(x=entry_bar + 2, y=avg_entry, text="Avg Entry",
                          style=label.style_label_left,
                          color="rgba(66,165,245,0.2)",
                          textcolor="#42a5f5", size="tiny")
