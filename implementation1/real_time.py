import numpy as np
import matplotlib.pyplot as plt
import scipy 
import soundfile
import sounddevice
from utilities import plot_dtft, fir_bpf, fir_lpf
import matplotlib


import os
import sys
import select
import tty
import termios

matplotlib.use('QtAgg') 


def get_key_nonblocking():
    """Polls stdin for a single character without blocking. This function was LLM-generated using Gemini 3.8 Flash"""
    dr, _, _ = select.select([sys.stdin], [], [], 0)
    if dr:
        return sys.stdin.read(1)
    return None



def resample(x, L, D, M):

    wc = min(np.pi / L, np.pi / D) # pi/160 from this
    h_gain = fir_lpf(wc, M, L)

    # to up-sample, we need to add L zeroes in between every point
    x_upsampled = np.zeros(len(x) * L, dtype=x.dtype)
    x_upsampled[::L] = x # standard python slice strat, as mentioned in lecture. every Lth point gets X vals, while everyhting else is zero

    x_filtered = scipy.signal.lfilter(h_gain, [1.0], x_upsampled, axis=0) # normalizes by 1 (no change) then filters x_upsampled points

    return x_filtered[::D] # decimate every point other than every Dth

def resample_rt(x, L, D, h_gain, zi):
    intermediate_len = len(x) * L
    x_upsampled = np.zeros(intermediate_len, dtype=np.float32)
    x_upsampled[::L] = x

    # 2. Convolve with lfilter using state tracking
    x_filtered, z_state_next = scipy.signal.lfilter(h_gain, [1.0], x_upsampled, zi=zi)

    # 3. Decimate by D
    y_chunk = x_filtered[::D]

    return y_chunk, z_state_next

def precompute_equalize(fs, M):
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



    return h_low, h_mid, h_high







if __name__ == '__main__':
    filename = input("Enter audio file name (with extension): \n")
    fs_in = 48000
    fs_out = 44100
    chunks = 4800
    M = 160 # we need to use lower M's here to account for delays
    L = 147
    D = 160
    wc = min(np.pi / L, np.pi / D)
    h_gain = fir_lpf(wc, M, L).astype(np.float32)
    zi_resample = np.zeros(len(h_gain) - 1, dtype=np.float32)
    

    h_low, h_mid, h_high = precompute_equalize(fs_in, M)
    zi_low = np.zeros(len(h_low) - 1, dtype=np.float32)
    zi_mid = np.zeros(len(h_mid) - 1, dtype=np.float32)
    zi_high = np.zeros(len(h_high) - 1, dtype=np.float32)

    g_low, g_mid, g_high = 1.0, 1.0, 1.0


    # This control print schema is also Gemini 3.8-Flash generated, as I thought it would come up with a better schema than I did and it seemed unimportant how the program parses input
    print("\n--- Live Controls (press key directly, no Enter needed) ---")
    print("  Low  (<300 Hz):     [q] -0.2   [w] +0.2")
    print("  Mid  (300Hz-2kHz):  [a] -0.2   [s] +0.2")
    print("  High (>2 kHz):      [z] -0.2   [x] +0.2")
    print("  Reset:              [r]")
    print("  Quit:               [ESC]\n")

    fd = sys.stdin.fileno() # C like stdin
    old_settings = termios.tcgetattr(fd)
    tty.setcbreak(fd) # ignores enter

    try:
        with soundfile.SoundFile(filename, 'r') as in_stream, sounddevice.OutputStream(samplerate=fs_out, channels=1) as out_stream: # https://python-sounddevice.readthedocs.io/en/0.3.14/examples.html
            while True:
                key = get_key_nonblocking()
                if key:
                    if key in ('\x1b', '\x03'):  # ESC or Ctrl+C
                        break
                    elif key == 'q': g_low = max(0.0, round(g_low - 0.2, 1)) # This control schema is also Gemini 3.8-Flash generated, as I thought it would come up with a better schema than I did and it seemed unimportant how the program parses input
                    elif key == 'w': g_low = min(3.0, round(g_low + 0.2, 1))
                    elif key == 'a': g_mid = max(0.0, round(g_mid - 0.2, 1))
                    elif key == 's': g_mid = min(3.0, round(g_mid + 0.2, 1))
                    elif key == 'z': g_high = max(0.0, round(g_high - 0.2, 1))
                    elif key == 'x': g_high = min(3.0, round(g_high + 0.2, 1))
                    elif key == 'r': g_low, g_mid, g_high = 1.0, 1.0, 1.0

                # 2. Real-time in-place status bar, Gemini 3.8
                sys.stdout.write(f"\r[Gains] Low: {g_low:3.1f}x | Mid: {g_mid:3.1f}x | High: {g_high:3.1f}x   ")
                sys.stdout.flush()
            

                



                data = in_stream.read(chunks, dtype='float32')
                if len(data) == 0:
                    break
                if data.ndim > 1:
                    x = np.mean(data, axis=1)
                else:
                    x = data

                if len(x) < chunks: # less song left than chunk size
                    pad_len = chunks - len(x)
                    x = np.pad(x, (0, pad_len))

                y_l, zi_low = scipy.signal.lfilter(h_low, [1.0], x, zi=zi_low) # feedback
                y_m, zi_mid = scipy.signal.lfilter(h_mid, [1.0], x, zi=zi_mid)
                y_h, zi_high = scipy.signal.lfilter(h_high, [1.0], x, zi=zi_high)
                x_eq = (g_low * y_l) + (g_mid * y_m) + (g_high * y_h)


                out, zi_resample = resample_rt(x_eq, L, D, h_gain, zi_resample)
                out_stream.write(out[:, None].astype(np.float32))
    finally:
        # restores terminal
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        print("\n\nPlayback terminated.")             




