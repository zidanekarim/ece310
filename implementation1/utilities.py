import numpy as np
import matplotlib.pyplot as plt
def plot_dtft(x):
    import numpy as np
    import matplotlib.pyplot as plt
    
    N = max(len(x), 100000)
    X = np.fft.fft(x, n=N)
    X = np.fft.fftshift(X)
    w = np.linspace(-np.pi, np.pi, N, endpoint=False)

    _, ax = plt.subplots(nrows=1, ncols=1, tight_layout=True)
    mag_ax = ax
    mag_ax.plot(w, np.abs(X), label=f'Case M={len(x)//2}')
    mag_ax.legend() # added this
    mag_ax.set_xticks(
        [-np.pi, -3*np.pi/4, -np.pi/2, -np.pi/4, 0, np.pi/4, np.pi/2, 3*np.pi/4, np.pi],
    )
    for x, label in [
        (-np.pi, r'$-\pi$'),
        (-np.pi/2, r'$-\pi/2$'),
        (np.pi/2, r'$\pi/2$'),
        (np.pi, r'$\pi$'),
    ]:
        mag_ax.annotate(
            label,
            xy=(x, 0),
            xycoords=('data', 'axes fraction'),
            xytext=(0, -25),
            textcoords='offset points',
            ha='center',
            va='top'
        )
    mag_ax.set_ylabel(r'|$X(\omega)$|')
    mag_ax.grid()
    mag_ax.set_xlim(-np.pi, np.pi)
    mag_ax.set_xlabel(r'$\omega$ (rad/sample)')

    plt.show()



def fir_lpf(wc, M, gain=1.0): # default gain is 1, this is because we will use this function again for the equalizers. 
    # Known info: f_intermediate = 7.056 MHz, wc will end up being pi/160, Passband Gain or H = 147. N=2M+1. Optimize for offline first, then choose an M such that real time works
    n = np.arange(-M, M+1, 1) # we are "windowing" only from -M to M, 2M + 1 numbers
    h = np.where(n == 0, wc / np.pi, np.sin(wc * n) / (np.pi * n))
    
    
    return gain * h # apply passband gain and return


def fir_bpf(h, wh, M):
    n = np.arange(-M, M+1, 1)
    return h * (2* np.cos(wh * n))





if __name__ == '__main__':
    # Example usage
    h = [1, 2, 3, 2, 1]
    plot_dtft(h)
