import numpy as np
import matplotlib.pyplot as plt

# Professor Aaron Langham's plot_dtft implementation
def plot_dtft(x):
    import numpy as np
    import matplotlib.pyplot as plt
    
    N = max(len(x), 100000)
    X = np.fft.fft(x, n=N)
    X = np.fft.fftshift(X)
    w = np.linspace(-np.pi, np.pi, N, endpoint=False)

    _, ax = plt.subplots(nrows=1, ncols=1, tight_layout=True)
    mag_ax = ax
    mag_ax.plot(w, np.abs(X), label='Magnitude')
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