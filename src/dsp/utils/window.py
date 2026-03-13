import numpy as np

def hann_window(N):
    return np.hanning(N)

def apply_window(x, window):
    return x * window