import numpy as np
import pyworld as pw                    # 新增：pip install pyworld
from scipy.signal import butter, lfilter, lfilter_zi

class PSOLAPitchShifter:
    def __init__(self, fs=44100, semitone=0.0):
        self.fs = fs
        self.semitone = semitone
        self.pitch_ratio = 2 ** (semitone / 12.0)
        self.fmin = 80
        self.fmax = 400

        # ====================== WORLD Harvest 参数 ======================
        self.f0_floor = 80
        self.f0_ceil = 400

        # ====================== 高通滤波（去电流声） ======================
        self.hp_cutoff = 80.0
        nyq = fs / 2
        b, a = butter(4, self.hp_cutoff / nyq, btype='high')
        self.b, self.a = b, a
        self.zi = None
        # ============================================================

    def set_semitone(self, semitone: float):
        self.semitone = semitone
        self.pitch_ratio = 2 ** (semitone / 12.0)

    def _estimate_f0(self, frame: np.ndarray):
        """用 WORLD Harvest（最推荐）求单值 F0"""
        if len(frame) < 256:
            return None

        x = frame.astype(np.float64)
        f0, _ = pw.harvest(x, self.fs, f0_floor=self.f0_floor, f0_ceil=self.fmax)

        voiced_f0 = f0[f0 > 0]
        if len(voiced_f0) == 0:
            return None
        return np.median(voiced_f0)  # ← 关键！取中值，最稳

    def process_block(self, input_block: np.ndarray) -> np.ndarray:
        frame = input_block.flatten().copy()
        if len(frame) < 256:
            return frame

        f0 = self._estimate_f0(frame)
        if f0 is None or f0 < self.fmin or f0 > self.fmax:
            return frame

        T = int(self.fs / f0)
        if T < 10 or 2 * T > len(frame):
            return frame

        marks = np.arange(T, len(frame) - T, T)
        if len(marks) < 2:
            return frame

        new_spacing = max(1, int(T / self.pitch_ratio))

        output = np.zeros(len(frame), dtype=np.float32)
        overlap_count = np.zeros(len(frame), dtype=np.float32)

        out_ptr = 0
        mark_index = 0
        while mark_index < len(marks) and out_ptr < len(frame):
            m = int(marks[mark_index])
            start = m - T
            end = m + T
            if start < 0 or end > len(frame):
                mark_index += 1
                continue

            segment = frame[start:end].copy()
            window = np.hanning(len(segment))
            segment *= window

            add_len = min(len(segment), len(output) - out_ptr)
            output[out_ptr:out_ptr + add_len] += segment[:add_len]
            overlap_count[out_ptr:out_ptr + add_len] += 1

            out_ptr += new_spacing
            mark_index += 1

        # === 核心：归一化（音量稳定 + 无电流声）===
        mask = overlap_count > 0
        output[mask] /= overlap_count[mask]
        output[~mask] = frame[~mask] * 0.5

        output -= np.mean(output)  # DC 去除

        # === 实时高通滤波（跨 block 无点击声）===
        if self.zi is None:
            self.zi = lfilter_zi(self.b, self.a)
        output, self.zi = lfilter(self.b, self.a, output, zi=self.zi)

        return output.reshape(input_block.shape)


# ====================== 使用示例 ======================
if __name__ == "__main__":
    import sounddevice as sd

    shifter = PSOLAPitchShifter(fs=44100, semitone=5)

    def callback(indata, outdata, frames, time, status):
        if status:
            print(status)
        block = indata[:, 0] if indata.ndim > 1 else indata
        processed = shifter.process_block(block)
        outdata[:] = processed[:, np.newaxis] if outdata.ndim > 1 else processed

    with sd.Stream(samplerate=44100, channels=1, blocksize=1024,
                   callback=callback):
        print("PSOLA + WORLD Harvest + 高通 已启动（声调正常，音质顶级）")
        input()