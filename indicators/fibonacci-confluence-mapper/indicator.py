from tg_scripting import *

zz_len = input.int(10, "Zigzag Length", minval=3, maxval=50)
num_swings = input.int(4, "Number of Swing Pairs", minval=2, maxval=8)
zone_width_atr = input.float(0.5, "Zone Width (ATR multiplier)")

fib_levels = [0.236, 0.382, 0.5, 0.618, 0.786]

swing_hi = ta.highest(high, zz_len)
swing_lo = ta.lowest(low, zz_len)

swing_high_prices = []
swing_low_prices = []
swing_high_bars = []
swing_low_bars = []

for i in range(200):
    if len(swing_high_prices) >= num_swings and len(swing_low_prices) >= num_swings:
        break
    h_val = float(high[i])
    l_val = float(low[i])
    sh_val = float(swing_hi[i])
    sl_val = float(swing_lo[i])
    if h_val == sh_val and len(swing_high_prices) < num_swings:
        if len(swing_high_prices) == 0 or abs(h_val - swing_high_prices[-1]) > 0.001:
            swing_high_prices.append(h_val)
            swing_high_bars.append(i)
    if l_val == sl_val and len(swing_low_prices) < num_swings:
        if len(swing_low_prices) == 0 or abs(l_val - swing_low_prices[-1]) > 0.001:
            swing_low_prices.append(l_val)
            swing_low_bars.append(i)

all_fib_prices = []
for sh in swing_high_prices:
    for sl in swing_low_prices:
        if abs(sh - sl) < 0.001:
            continue
        swing_range = sh - sl
        for fib in fib_levels:
            all_fib_prices.append(sh - swing_range * fib)
            all_fib_prices.append(sl + swing_range * fib)

atr_val = ta.atr(high, low, close, 14)
bucket_size = float(atr_val[0]) * zone_width_atr

strongest_zone_price = float(close[0])
second_zone_price = float(close[0])
strongest_count = 0
second_count = 0
confluence_strength = 0.0

if bucket_size > 0 and len(all_fib_prices) > 0:
    sorted_fibs = sorted(all_fib_prices)
    zones = []
    current_zone = [sorted_fibs[0]]
    for j in range(1, len(sorted_fibs)):
        if sorted_fibs[j] - current_zone[0] <= bucket_size:
            current_zone.append(sorted_fibs[j])
        else:
            zones.append(current_zone)
            current_zone = [sorted_fibs[j]]
    zones.append(current_zone)

    best_zones = []
    for zone in zones:
        count = len(zone)
        avg_price = sum(zone) / count
        if count >= 3:
            best_zones.append((count, avg_price))
    best_zones.sort(reverse=True)

    if len(best_zones) >= 1:
        strongest_count = best_zones[0][0]
        strongest_zone_price = best_zones[0][1]
    if len(best_zones) >= 2:
        second_count = best_zones[1][0]
        second_zone_price = best_zones[1][1]

    cur_price = float(close[0])
    for fp in all_fib_prices:
        if abs(fp - cur_price) <= bucket_size:
            confluence_strength = confluence_strength + 1.0

if strongest_count >= 3:
    hline(strongest_zone_price, title="Confluence Zone 1", color="rgba(255, 215, 0, 0.9)")

if second_count >= 3:
    hline(second_zone_price, title="Confluence Zone 2", color="rgba(0, 188, 212, 0.9)")

if len(swing_high_prices) > 0 and len(swing_low_prices) > 0:
    sh_bar = swing_high_bars[0]
    sh_price = swing_high_prices[0]
    sl_price = swing_low_prices[0]
    swing_range = sh_price - sl_price
    for fib in fib_levels:
        fib_price = sh_price - swing_range * fib
        line.new(x1=-sh_bar, y1=fib_price, x2=0, y2=fib_price, color="rgba(255, 215, 0, 0.3)")

in_zone = False
if strongest_count >= 3 and bucket_size > 0:
    if abs(float(close[0]) - strongest_zone_price) <= bucket_size:
        in_zone = True
if second_count >= 3 and bucket_size > 0:
    if abs(float(close[0]) - second_zone_price) <= bucket_size:
        in_zone = True

bgcolor_color = "rgba(255, 215, 0, 0.1)" if in_zone else "rgba(0, 0, 0, 0)"
bgcolor(close, color=bgcolor_color)

plot(confluence_strength, title="Confluence Strength", color="rgba(0, 188, 212, 0.8)")
