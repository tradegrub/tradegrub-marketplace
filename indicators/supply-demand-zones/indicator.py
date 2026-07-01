from tg_scripting import *

indicator("Supply Demand Zones", overlay=True)

lookback = input.int(20, "Lookback", minval=5, maxval=100)
atr_len = input.int(14, "ATR Length", minval=5, maxval=50)
strength = input.float(2.0, "Departure Strength", minval=1.0, maxval=5.0)
show_labels = input.bool(True, "Show Labels")
show_levels = input.bool(True, "Show Levels")
max_zones = input.int(5, "Max Zones", minval=1, maxval=20)
zone_opacity = input.int(80, "Zone Opacity", minval=10, maxval=100)
show_supply = input.bool(True, "Show Supply Zones")
show_demand = input.bool(True, "Show Demand Zones")
mitigated_style = input.bool(True, "Dim Mitigated Zones")

atr = ta.atr(high, low, close, atr_len)
threshold = atr * strength

bearish_departure = (open - close > threshold) & (high == ta.highest(high, lookback))
bullish_departure = (close - open > threshold) & (low == ta.lowest(low, lookback))

supply_zones = []
demand_zones = []

for i in range(len(close)):
    if show_supply and bearish_departure[i]:
        supply_zones.append({"top": high[i], "bot": open[i], "start": i, "active": True})
    if show_demand and bullish_departure[i]:
        demand_zones.append({"top": open[i], "bot": low[i], "start": i, "active": True})

    for z in supply_zones:
        if z["active"] and close[i] > z["top"]:
            z["active"] = False
    for z in demand_zones:
        if z["active"] and close[i] < z["bot"]:
            z["active"] = False

    supply_zones = [z for z in supply_zones if z["active"] or (mitigated_style and i - z["start"] < lookback * 3)]
    demand_zones = [z for z in demand_zones if z["active"] or (mitigated_style and i - z["start"] < lookback * 3)]

    supply_zones = supply_zones[-max_zones:]
    demand_zones = demand_zones[-max_zones:]

supply_sig = bearish_departure
demand_sig = bullish_departure
plotshape(supply_sig, title="Supply Zone", shape="triangledown", location="abovebar", color="red", size="small")
plotshape(demand_sig, title="Demand Zone", shape="triangleup", location="belowbar", color="green", size="small")

# --- Rich annotations ---
import numpy as np
n = len(close)
last_supply_label_idx = -100
last_demand_label_idx = -100
cooldown_bars = lookback

for i in range(lookback, n):
    if show_labels and bearish_departure[i] and (i - last_supply_label_idx) > cooldown_bars:
        last_supply_label_idx = i
        label.new(
            x=i, y=float(high[i]),
            text="Supply",
            style=label.style_label_down,
            color="rgba(239,83,80,0.25)",
            textcolor="#ef5350",
            size="small"
        )
        if show_levels:
            end_bar = min(i + lookback * 2, n - 1)
            box.new(left=i, top=float(high[i]), right=end_bar, bottom=float(open[i]),
                    border_color="rgba(239,83,80,0.2)", bgcolor="rgba(239,83,80,0.04)")
            line.new(x1=i, y1=float(high[i]), x2=end_bar, y2=float(high[i]),
                     color="#ef5350", width=1, style=line.style_dashed)

    if show_labels and bullish_departure[i] and (i - last_demand_label_idx) > cooldown_bars:
        last_demand_label_idx = i
        label.new(
            x=i, y=float(low[i]),
            text="Demand",
            style=label.style_label_up,
            color="rgba(0,230,118,0.25)",
            textcolor="#00e676",
            size="small"
        )
        if show_levels:
            end_bar = min(i + lookback * 2, n - 1)
            box.new(left=i, top=float(open[i]), right=end_bar, bottom=float(low[i]),
                    border_color="rgba(0,230,118,0.2)", bgcolor="rgba(0,230,118,0.04)")
            line.new(x1=i, y1=float(low[i]), x2=end_bar, y2=float(low[i]),
                     color="#00e676", width=1, style=line.style_dashed)
