import sounddevice as sd

class AudioStream:
    def __init__(self, fs, block_size, processor):
        self.fs = fs
        self.block_size = block_size
        self.processor = processor

    def callback(self, indata, outdata, frames, time, status):

        input_block = indata[:,0]

        processed = self.processor.process(input_block)

        outdata[:] = processed.reshape(-1,1)

    def start(self):

        self.stream = sd.Stream(
            samplerate=self.fs,
            blocksize=self.block_size,
            channels=1,
            callback=self.callback
        )

        self.stream.start()