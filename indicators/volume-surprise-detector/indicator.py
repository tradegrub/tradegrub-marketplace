from tg_scripting import *
import numpy as np

lookback = input.int(20, "Lookback Period", minval=5, maxval=200)
surprise_threshold = input.float(2.0, "Surprise Threshold (Z-Score)")

expected_vol = ta.sma(volume, lookback)

vol_diff_sq = (volume - expected_vol) ** 2
vol_variance = ta.sma(vol_diff_sq, lookback)
vol_std = np.sqrt(np.maximum(np.array(vol_variance, dtype=float), 1.0))

z_score = (np.array(volume, dtype=float) - np.array(expected_vol, dtype=float)) / vol_std

positive_surprise = z_score > surprise_threshold
negative_surprise = z_score < -surprise_threshold

plot(z_score, title="Volume Z-Score", color="#2196F3")
hline(0, title="Zero", color="#555555")
hline(surprise_threshold, title="Positive Threshold", color="#4CAF50")
hline(-surprise_threshold, title="Negative Threshold", color="#F44336")
plotshape(positive_surprise, title="Positive Surprise", style="triangleup", location="belowbar", color="#4CAF50")
plotshape(negative_surprise, title="Negative Surprise", style="triangledown", location="abovebar", color="#F44336")

extreme_pos = z_score > (surprise_threshold + 1)
extreme_neg = z_score < -(surprise_threshold + 1)
bgcolor(extreme_pos, color="rgba(76, 175, 80, 0.15)")
bgcolor(extreme_neg, color="rgba(244, 67, 54, 0.15)")
