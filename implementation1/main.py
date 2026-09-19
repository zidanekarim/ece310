import numpy as np
import matplotlib.pyplot as plt
import scipy 
import soundfile
from utilities import plot_dtft, fir_bpf, fir_lpf
import matplotlib

matplotlib.use('QtAgg')     # because i ran this in a venv


M_vals = (10, 100, 1000, 10000)
#M_vals =(1000000000,) for some reason this crashed my VSCode!
#M_vals =(10000000,)

wc = np.pi / 160 # 0.0196 rad/s, using w bc it seems the plot_dtft operates in rad/s

for M in M_vals:
    n = np.arange(-M, M+1, 1) # arange bc discrete points. Also hate that this is called arange over arrange
    # closed form analytical expression, sin(wc*n) / pi*n
    h = np.where(n == 0, wc / np.pi, np.sin(wc * n) / (np.pi * n)) # Given: treat h[0] as wc/pi. so no division by n will even occur (ignore runtime warning)

    plot_dtft(h)





def resample(x, L, D, M):

    wc = min(np.pi / L, np.pi / D) # pi/160 from this
    h_gain = fir_lpf(wc, M, L)

    # to up-sample, we need to add L zeroes in between every point
    x_upsampled = np.zeros(len(x) * L, dtype=x.dtype)
    x_upsampled[::L] = x # standard python slice strat, as mentioned in lecture. every Lth point gets X vals, while everyhting else is zero

    x_filtered = scipy.signal.lfilter(h_gain, [1.0], x_upsampled, axis=0) # normalizes by 1 (no change) then filters x_upsampled points

    return x_filtered[::D] # decimate every point other than every Dth


def equalize(x, fs, M, g_low, g_mid, g_high):
    pi = np.pi
    wl = 2*pi* (300/fs)
    wm = 2*pi* (2000 / fs)
    wh = 2*pi* (20000 / fs) # frequencies from assignment chart

    h_low = fir_lpf(wl, M, gain=1)

    # now we need a filter that passes btwn 300Hz and 2kHz, but fir_lpf centers at 0hz and has a span from -wc to wc
    # calculate new center freq -> (300 + 2000) / 2  = 1150 Hz. our BPF function expects this frequency 
    # calculate new cutoff -> remember for LPF, we span from -wc to wc (width 2wc.) we want 2wc = |300-2000|. solve for wc, wc = 850Hz, so we span from -850 to 850.
    # now look -> 1150 + 850 = 2000, 1150-850 = 300
    w_center_mid = (wl + wm) / 2 
    w_cutoff_mid = (wm - wl) / 2 
    h_mid = fir_bpf(fir_lpf(w_cutoff_mid, M, 1), w_center_mid, M)

    w_center_high = (wm + wh) / 2 
    w_cutoff_high = (wh - wm) / 2 
    h_high = fir_bpf(fir_lpf(w_cutoff_high, M, 1), w_center_high, M)


    y_low = scipy.signal.lfilter(h_low, [1.0], x, axis=0)
    y_mid = scipy.signal.lfilter(h_mid, [1.0], x, axis=0)
    y_high = scipy.signal.lfilter(h_high, [1.0], x, axis=0)

    return (g_low * y_low) + (g_mid * y_mid) + (g_high * y_high) # see summation diagram 







if __name__ == '__main__':
    filename = input("Enter audio file name (with extension): \n")


    # I used an LLM to scour through the soundfile documentation to load the output file. LLM used: Google's Gemma4, ran from Cooper Union EE Servers. 
    # This is because I wanted to make sure I did not resample the audio by accident while inputting, which defeats the problem, since a previous lib I used (librosa) did this
    data, sampling_rate = soundfile.read(filename)
    if data.ndim > 1:
        data = data.mean(axis=1)
    data = data.astype(np.float32)
    
    print(f"Initial sampling rate of {filename} is {sampling_rate/1000} kHz")

    equalized = equalize(data, sampling_rate, 300, 5, 5, 5)
    resampled = resample(equalized, 147, 160, 1000)


    # we need to volume normalize if we changed gain at any point , (g_low * y_low) + (g_mid * y_mid) + (g_high * y_high)
    max = np.max(np.abs(resampled))
    # -1, 1 range
    if max >0:
        resampled /= max
    
    soundfile.write("output.wav", resampled, 44100, subtype='PCM_16') # from soundfile docs, default subtype for WAV files


    print("Finished!")



