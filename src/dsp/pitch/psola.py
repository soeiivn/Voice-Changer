import numpy as np
import soundfile as sf
import os

# 如不存在voice.wav，就生成一个测试音频
if not os.path.exists("voice.wav"):
    print("生成测试音频文件...")
    fs = 16000  # 采样率
    duration = 2 # 2秒

    # 生成一个简单的元音序列（100Hz的基频）
    t = np.linspace(0, duration, int(fs * duration))

    # 模拟元音a: 基频100Hz + 谐波
    f0 = 100  # 基频
    audio = (np.sin(2 * np.pi * f0 * t) +  # 基频
             0.5 * np.sin(2 * np.pi * 2 * f0 * t) +  # 二次谐波
             0.3 * np.sin(2 * np.pi * 3 * f0 * t) +  # 三次谐波
             0.1 * np.sin(2 * np.pi * 4 * f0 * t))  # 四次谐波

    # 添加包络（让声音更自然）
    envelope = np.exp(-t / 0.5)  # 衰减包络
    audio = audio * envelope

    # 保存为wav文件
    sf.write("voice.wav", audio, fs)
    print("测试音频已生成: voice.wav")
else:
    print("找到现有voice.wav文件")

audio, fs = sf.read("voice.wav")
print(f"音频加载成功: 长度={len(audio)}点, 采样率={fs}Hz")

class PSOLAPitchShifter:
    def __init__(self, fs, semitone=0):
        self.fs = fs
        self.semitone = semitone

    def process(self, frame):
        f0 = self._estimate_f0(frame)
        if f0 is None:
            return frame
        return self._psola(frame, f0)

    def _estimate_f0(self, frame, fmin=80, fmax=400):
        frame = frame - np.mean(frame)

        if np.max(np.abs(frame)) < 1e-3:
            return None

        autocorr = np.correlate(frame, frame, mode='full')
        autocorr = autocorr[len(autocorr)//2:]

        min_lag = int(self.fs / fmax)
        max_lag = int(self.fs / fmin)

        if max_lag >= len(autocorr):
            return None

        lag = np.argmax(autocorr[min_lag:max_lag]) + min_lag
        return self.fs / lag

    def _psola(self, frame, f0):
        pitch_ratio = 2 ** (self.semitone / 12)

        T = int(self.fs / f0)
        T_new = int(T / pitch_ratio)

        output = np.zeros(len(frame) + 2 * T)
        weight = np.zeros(len(frame) + 2 * T)

        marks = np.arange(T, len(frame) - T, T)
        marks = self._refine_marks(frame, marks, T)

        for i, m in enumerate(marks):
            start = m - T
            end = m + T

            if start < 0 or end > len(frame):
                continue

            segment = frame[start:end]

            window = np.hanning(len(segment))
            segment = segment * window

            new_m = int(i * T_new + T)
            new_start = new_m - T
            new_end = new_m + T

            if new_start < 0 or new_end > len(output):
                continue

            output[new_start:new_end] += segment
            weight[new_start:new_end] += window

        # 避免除0
        nonzero = weight > 0.5
        output[nonzero] /= weight[nonzero]

        return output[:len(frame)]

    def _refine_marks(self, frame, marks, T):
        refined = []

        search_radius = int(0.2 * T)

        for m in marks:
            start = max(m - search_radius, 0)
            end = min(m + search_radius, len(frame))

            segment = frame[start:end]

            if len(segment) == 0:
                continue

            peak = np.argmax(np.abs(segment))
            refined_mark = start + peak

            refined.append(refined_mark)

        return np.array(refined)

if __name__ == "__main__":
    audio, fs = sf.read("voice.wav")
    print(f"原始音频: 长度={len(audio)}点, 时长={len(audio) / fs:.2f}秒, 采样率={fs}Hz")

    # 如果是双声道，转单声道
    if len(audio.shape) > 1:
        audio = audio[:, 0]
        print(f"转换为单声道: {audio.shape}")

    shifter = PSOLAPitchShifter(fs, semitone=+2)
    print(f"变调器: 半音偏移={shifter.semitone}")

    # 测试整段
    print("正在处理音频...")
    output = shifter.process(audio)

    print(f"处理后音频: 长度={len(output)}点, 时长={len(output) / fs:.2f}秒")
    print(f"原始长度: {len(audio)} → 处理后长度: {len(output)}")
    print(f"长度变化比例: {len(output) / len(audio):.3f}")

    sf.write("shifted.wav", output, fs)
    print("已保存: shifted.wav")