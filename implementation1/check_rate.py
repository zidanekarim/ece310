import numpy as np
import matplotlib.pyplot as plt
import scipy 
import soundfile
from utilities import plot_dtft, fir_bpf, fir_lpf
import matplotlib

if __name__ == '__main__':
    filename = input("Enter audio file name (with extension): \n")


    data, sampling_rate = soundfile.read(filename)
    

    
    print(f"Initial sampling rate of {filename} is {sampling_rate/1000} kHz")