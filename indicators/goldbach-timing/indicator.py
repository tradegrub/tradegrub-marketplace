from tg_scripting import *
import numpy as np

swing_threshold = input.float(2.0, "Swing Threshold (ATR mult)", minval=0.5, maxval=10.0)

src_close = np.array(close, dtype=float)
src_high = np.array(high, dtype=float)
src_low = np.array(low, dtype=float)
n = len(src_close)

# ATR
atr_vals = ta.atr(high, low, close, 14)
atr_arr = np.array(atr_vals, dtype=float)

# Generate primes up to a reasonable limit using sieve
def sieve_primes(limit):
    if limit < 2:
        return set()
    is_prime = np.ones(limit + 1, dtype=bool)
    is_prime[0] = is_prime[1] = False
    for i in range(2, int(limit ** 0.5) + 1):
        if is_prime[i]:
            is_prime[i * i::i] = False
    return set(np.where(is_prime)[0])

primes = sieve_primes(500)

# Fibonacci numbers up to 500
fibs = set()
a, b = 1, 1
while a <= 500:
    fibs.add(a)
    a, b = b, a + b

# Track swings and count bars since last swing
bars_since_swing = np.zeros(n, dtype=int)
last_swing_idx = 0

for i in range(1, n):
    change = abs(src_close[i] - src_close[last_swing_idx])
    threshold = atr_arr[i] * swing_threshold
    if change >= threshold:
        last_swing_idx = i
        bars_since_swing[i] = 0
    else:
        bars_since_swing[i] = i - last_swing_idx

# Timing score: proximity to next prime count
timing_score = np.zeros(n, dtype=float)
is_prime_bar = np.zeros(n, dtype=bool)
is_fib_bar = np.zeros(n, dtype=bool)

sorted_primes = sorted(primes)

for i in range(n):
    count = bars_since_swing[i]
    if count in primes:
        is_prime_bar[i] = True
    if count in fibs:
        is_fib_bar[i] = True

    # Find distance to next prime
    dist_to_next = 100
    for p in sorted_primes:
        if p >= count:
            dist_to_next = p - count
            break

    # Score: higher when close to a prime, bonus for Fibonacci overlap
    if dist_to_next == 0:
        timing_score[i] = 100.0
    else:
        timing_score[i] = max(0, 100.0 - dist_to_next * 10)

    if count in fibs and count in primes:
        timing_score[i] = 100.0  # Prime-Fibonacci confluence

plot(timing_score, title="Timing Score", color="#ffab40")
hline(80, title="High Alert", color="#ff1744")
hline(50, title="Moderate", color="#ffc107")

plotshape(is_prime_bar, title="Prime Bar", style="triangleup", location="belowbar", color="#e040fb")
