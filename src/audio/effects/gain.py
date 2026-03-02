import numpy as np
from .base import Effect

class Gain:
    def __init__(self, gain=1.0):
        self.gain = gain

    def set_gain(self, value):
        self.gain = value

    def process(self, audio):
        processed = audio * self.gain
        return np.clip(processed, -1.0, 1.0)