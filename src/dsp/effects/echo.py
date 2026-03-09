import numpy as np
import sounddevice as sd

# ==========================================
# Delay Echo Effect
# ==========================================
class EchoEffect:

    def __init__(self, fs, delay_ms=250, decay=0.4):

        self.fs = fs
        self.delay_samples = int(fs * delay_ms / 1000)

        self.decay = decay

        self.buffer = np.zeros(self.delay_samples)
        self.ptr = 0

    def process_block(self, input_block):

        output = np.zeros_like(input_block)

        for i in range(len(input_block)):

            delayed = self.buffer[self.ptr]

            y = input_block[i] + self.decay * delayed

            output[i] = y

            self.buffer[self.ptr] = input_block[i]

            self.ptr += 1
            if self.ptr >= self.delay_samples:
                self.ptr = 0

        return output

fs = 16000
block_size = 1024

echo = EchoEffect(fs, delay_ms=300, decay=0.5)

def callback(indata, outdata, frames, time, status):

    input_block = indata[:,0]

    processed = echo.process_block(input_block)

    outdata[:] = processed.reshape(-1,1)

print("🎤 Echo Effect Start")

with sd.Stream(
        samplerate=fs,
        blocksize=block_size,
        channels=1,
        dtype='float32',
        callback=callback):

    while True:
        sd.sleep(1000)