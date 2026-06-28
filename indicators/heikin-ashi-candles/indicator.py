from tg_scripting import *

show_real = input.bool(False, "Show Real Candles Too")

ha_close = (open + high + low + close) / 4
ha_open = ta.sma((open + close) / 2, 2)
ha_high = ta.highest(high, 1)
ha_low = ta.lowest(low, 1)

plotcandle(ha_open, ha_high, ha_low, ha_close, title="Heikin-Ashi")
