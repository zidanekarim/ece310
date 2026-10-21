import numpy as np
import matplotlib.pyplot as plt
import scipy
import scipy.signal as signal
from utilities import plot_dtft



# FIR differentiator 

M = 50
# group delay => M/2 = 25
group_delay = M/2
wd = 0.7 * np.pi
h = signal.remez(M+1, [0, 0.7 * 0.5], wd, type="differentiator", fs=1)

print(f"Group delay: {group_delay} samples")
print("Filter coefficients h[n]:\n", h)

# sampling freq is 256 khz
# so nyquist freq is 128 khz

# wd < pi
# we want the ideal region to be more than dont care: let's pick 0.7pi as wd



print(f"Group Delay of FIR differentiator: {}")