from tg_scripting import *
import numpy as np

indicator("Volume Spread Analysis", overlay=False)

vol_avg_len = input.int(20, "Volume Average Length", minval=5, maxval=100)
spread_avg_len = input.int(20, "Spread Average Length", minval=5, maxval=100)
high_vol_mult = input.float(1.5, "High Volume Multiplier", minval=1.0, maxval=3.0, step=0.1)
low_vol_mult = input.float(0.5, "Low Volume Multiplier", minval=0.1, maxval=1.0, step=0.1)
show_labels = input.bool(True, "Show Signal Labels")

close_arr = np.array(close, dtype=float)
open_arr = np.array(open, dtype=float)
high_arr = np.array(high, dtype=float)
low_arr = np.array(low, dtype=float)
vol_arr = np.array(volume, dtype=float)

spread = high_arr - low_arr
body = np.abs(close_arr - open_arr)
is_up = close_arr > open_arr
is_down = close_arr < open_arr

avg_vol = ta.sma(volume, vol_avg_len)
avg_spread = ta.sma(spread.tolist(), spread_avg_len)

avg_vol_arr = np.array(avg_vol, dtype=float)
avg_spread_arr = np.array(avg_spread, dtype=float)

rel_vol = np.where(avg_vol_arr > 0, vol_arr / avg_vol_arr, 1.0)
rel_spread = np.where(avg_spread_arr > 0, spread / avg_spread_arr, 1.0)

vsa_score = np.zeros(len(close))

# Supply: high volume + wide spread + down close
supply = (rel_vol > high_vol_mult) & is_down & (rel_spread > 1.0)
# Demand: high volume + wide spread + up close
demand = (rel_vol > high_vol_mult) & is_up & (rel_spread > 1.0)
# No demand: low volume + narrow spread + down close
no_demand = (rel_vol < low_vol_mult) & is_down & (rel_spread < 1.0)
# No supply: low volume + narrow spread + up close
no_supply = (rel_vol < low_vol_mult) & is_up & (rel_spread < 1.0)

vsa_score = np.where(demand, rel_vol * rel_spread, vsa_score)
vsa_score = np.where(supply, -rel_vol * rel_spread, vsa_score)
vsa_score = np.where(no_demand, -0.5, vsa_score)
vsa_score = np.where(no_supply, 0.5, vsa_score)

colors = []
for v in vsa_score:
    if v > 0.5:
        colors.append("#00e676")
    elif v < -0.5:
        colors.append("#ff1744")
    elif v > 0:
        colors.append("rgba(0,230,118,0.4)")
    elif v < 0:
        colors.append("rgba(255,23,68,0.4)")
    else:
        colors.append("#555555")

plot(vsa_score.tolist(), title="VSA Score", color="#42A5F5", linewidth=2)
plot(rel_vol.tolist(), title="Relative Volume", color="#FFA726", linewidth=1)
hline(0.0, title="Zero", color="#555555", linestyle="dashed")
hline(1.5, title="High Vol", color="#00e676", linestyle="dashed")
hline(-1.5, title="High Supply", color="#ff1744", linestyle="dashed")

if show_labels:
    demand_arr = demand.tolist()
    supply_arr = supply.tolist()
    plotshape(demand_arr, title="Demand", style="triangleup", location="bottom", color="#00e676")
    plotshape(supply_arr, title="Supply", style="triangledown", location="top", color="#ff1744")
