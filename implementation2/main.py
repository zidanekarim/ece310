
import numpy as np
import matplotlib
matplotlib.use('QtAgg') 

import matplotlib.pyplot as plt
import scipy
import scipy.signal as signal
from utilities import plot_dtft
import soundfile


path = "./audio/"
i = 1
data = scipy.io.loadmat(path + f"baseband{i}.mat")
#print(data.keys())
data = np.asarray(data["data"]).squeeze()
# FIR differentiator 

M = 50
# group delay => M/2 = 25
group_delay = M/2

def limiter(data):
    magnitude = np.abs(data)
    return magnitude/data # normalized to prevent blowup


# sampling freq is 256 khz
# so nyquist freq is 128 khz

# wd < pi
# we want the ideal region to be more than dont care: let's pick 0.7pi as wd


wd = 0.7 * np.pi
f_d = wd / (2 * np.pi) # normalized freq
h = signal.remez(
    M + 1,
    [0, f_d],
    [2*np.pi],
    type="differentiator",
    fs=1
)

plot_dtft(h)

print(f"Group delay: {group_delay} samples")
#print("Filter coefficients h[n]:\n", h)

plot_dtft(limiter(data))

conjugate = np.conj(limiter(data))
# now apply delay to the conjugate signal
delayed_conjugate = np.concatenate((np.zeros(int(group_delay)), conjugate[:-int(group_delay)]))
differentiated = signal.lfilter(h, 1, limiter(data))
y_n = np.imag(delayed_conjugate * differentiated)


## deemphasis filter
tau = 75e-6
fs = 256e3

b = [1/(1 + 150e-6*fs)] * 2
a = [1, (1 - 150e-6*fs)/(1 + 150e-6*fs)]

y = signal.lfilter(b, a, y_n)

plot_dtft(y)

f_pass = 15e3
f_stop = 18e3 # we want to stop before the 19khz so we dont get the pilot tone. 19 < 23 so by doing this we already filter out stereo. 
M_lpf = 300
lpf = signal.remez(M_lpf+1, [0, f_pass, f_stop, fs/2], [1, 0], weight=[1,10], fs=fs)

plot_dtft(lpf)

y_lpf = signal.lfilter(lpf, 1, y)
y_out = y_lpf[::4] # decimate by 4 to get 64kHz output

plot_dtft(y_out)


max_val = np.max(np.abs(y_out))
if max_val > 0:
    y_out = 0.99 * (y_out / max_val)
 
soundfile.write("output.wav", y_out, 64000, subtype='PCM_16') # from soundfile docs, default subtype for WAV files