from tg_scripting import *

length = input.int(50, "Lookback Length", minval=10, maxval=200)
show_fill = input.bool(True, "Show Fill Between Bands")

hi = ta.highest(high, length)
lo = ta.lowest(low, length)
rng = hi - lo

fib_236 = lo + rng * 0.236
fib_382 = lo + rng * 0.382
fib_500 = lo + rng * 0.500
fib_618 = lo + rng * 0.618
fib_786 = lo + rng * 0.786

p_hi = plot(hi, title="High", color="#B71C1C")
p_786 = plot(fib_786, title="Fib 78.6%", color="#EF5350")
p_618 = plot(fib_618, title="Fib 61.8%", color="#FF7043")
p_500 = plot(fib_500, title="Fib 50.0%", color="#FF9800")
p_382 = plot(fib_382, title="Fib 38.2%", color="#66BB6A")
p_236 = plot(fib_236, title="Fib 23.6%", color="#26A69A")
p_lo = plot(lo, title="Low", color="#004D40")

fill(p_618, p_382, color="rgba(255,152,0,0.08)")
