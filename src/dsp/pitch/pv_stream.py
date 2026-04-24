import numpy as np


class PVStream:
    def __init__(self, pv, frame_size=512, hop=128, fs = 48000):
        self.pv = pv
        self.frame_size = frame_size
        self.hop = hop

        self.in_buffer = np.zeros(0, dtype=np.float32)
        self.ola_buffer = np.zeros(frame_size, dtype=np.float32)
        self.out_buffer = np.zeros(0, dtype=np.float32)

        self.window = np.hanning(frame_size)

    def process(self, x: np.ndarray, semitone: float):
        if len(x) == 0:
            return x

        ratio = 2 ** (semitone / 12.0)

        self.in_buffer = np.concatenate([self.in_buffer, x])

        outputs = []

        while len(self.in_buffer) >= self.frame_size:
            frame = self.in_buffer[:self.frame_size]
            self.in_buffer = self.in_buffer[self.hop:]

            # ✅ 不重复 window
            y = self.pv.process_frame(frame, ratio)

            # ✅ OLA
            y *= self.window
            self.ola_buffer += y

            outputs.append(self.ola_buffer[:self.hop].copy())

            self.ola_buffer[:-self.hop] = self.ola_buffer[self.hop:]
            self.ola_buffer[-self.hop:] = 0.0

        if outputs:
            self.out_buffer = np.concatenate(
                [self.out_buffer, np.concatenate(outputs)]
            )

        # ✅ 严格长度匹配（关键防崩）
        needed = len(x)

        if len(self.out_buffer) >= needed:
            out = self.out_buffer[:needed]
            self.out_buffer = self.out_buffer[needed:]
        else:
            pad = np.zeros(needed - len(self.out_buffer), dtype=np.float32)
            out = np.concatenate([self.out_buffer, pad])
            self.out_buffer = np.zeros(0, dtype=np.float32)

        return out.astype(np.float32)