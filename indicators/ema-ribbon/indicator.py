from tg_scripting import *

ema8 = ta.ema(close, 8)
ema13 = ta.ema(close, 13)
ema21 = ta.ema(close, 21)
ema34 = ta.ema(close, 34)
ema55 = ta.ema(close, 55)
ema89 = ta.ema(close, 89)

p1 = plot(ema8, title="EMA 8", color="rgba(0,188,212,0.9)")
p2 = plot(ema13, title="EMA 13", color="rgba(0,150,136,0.9)")
p3 = plot(ema21, title="EMA 21", color="rgba(76,175,80,0.9)")
p4 = plot(ema34, title="EMA 34", color="rgba(255,193,7,0.9)")
p5 = plot(ema55, title="EMA 55", color="rgba(255,87,34,0.9)")
p6 = plot(ema89, title="EMA 89", color="rgba(244,67,54,0.9)")

fill(p1, p2, color="rgba(0,188,212,0.08)")
fill(p2, p3, color="rgba(0,150,136,0.08)")
fill(p3, p4, color="rgba(76,175,80,0.08)")
fill(p4, p5, color="rgba(255,193,7,0.08)")
fill(p5, p6, color="rgba(255,87,34,0.08)")
