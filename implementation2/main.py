import numpy as np
import matplotlib.pyplot as plt
import scipy
import scipy.signal as signal
from utilities import plot_dtft



# FIR differentiator 

M = 50
signal.remez(M+1)

# sampling freq is 256 khz
# so nyquist freq is 128 khz
# SDRs typically 


print(f"Group Delay of FIR differentiator: {}")