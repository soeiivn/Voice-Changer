import numpy as np

def estimate_f0(frame, fs, fmin=80, fmax=400):

    frame = frame - np.mean(frame)

    energy = np.sqrt(np.mean(frame ** 2))
    if energy < 1e-4:
        return None

    autocorr = np.correlate(frame, frame, mode='full')
    autocorr = autocorr[len(autocorr)//2:]

    min_lag = int(fs / fmax)
    max_lag = int(fs / fmin)

    if max_lag >= len(autocorr):
        return None

    lag = np.argmax(autocorr[min_lag:max_lag]) + min_lag

    return fs / lag