import numpy as np
import sounddevice as sd
import sys


class RealtimePSOLA:

    def __init__(self, fs, semitone=0):

        self.fs = fs
        self.pitch_ratio = 2 ** (semitone / 12)

        # 分析缓冲
        self.buffer_size = 4096
        self.buffer = np.zeros(self.buffer_size)
        self.write_ptr = 0

        # 上次周期
        self.prev_f0 = 150
        self.T = int(fs / self.prev_f0)

    # ==========================
    # 主处理函数
    # ==========================
    def process_block(self, input_block):

        N = len(input_block)

        # 写入环形缓冲
        for i in range(N):
            self.buffer[self.write_ptr] = input_block[i]
            self.write_ptr = (self.write_ptr + 1) % self.buffer_size

        frame = self._get_recent_frame(2048)

        f0 = self._estimate_f0(frame)

        if f0 is not None:
            self.prev_f0 = 0.9 * self.prev_f0 + 0.1 * f0

        T = int(self.fs / self.prev_f0)
        T = np.clip(T, 40, 400)

        # pitch marks
        marks = np.arange(T, len(frame) - T, T)

        if len(marks) < 2:
            return input_block

        output = np.zeros(N)
        out_ptr = 0
        mark_index = 0

        new_spacing = int(T / self.pitch_ratio)

        while out_ptr < N and mark_index < len(marks):

            m = int(marks[mark_index])

            start = m - T
            end = m + T

            if start < 0 or end > len(frame):
                mark_index += 1
                continue

            segment = frame[start:end].copy()

            window = np.hanning(len(segment))
            segment *= window

            seg_len = len(segment)

            if out_ptr + seg_len > N:
                break

            output[out_ptr:out_ptr + seg_len] += segment

            out_ptr += new_spacing
            mark_index += 1

        # 音量匹配
        in_energy = np.sqrt(np.mean(input_block ** 2))
        out_energy = np.sqrt(np.mean(output ** 2))

        if out_energy > 1e-6:
            output *= in_energy / out_energy

        if np.max(np.abs(output)) < 1e-6:
            return input_block

        return output

    # ==========================
    # 最近帧
    # ==========================
    def _get_recent_frame(self, length):

        if self.write_ptr - length >= 0:
            return self.buffer[self.write_ptr - length:self.write_ptr]

        part1 = self.buffer[self.write_ptr - length:]
        part2 = self.buffer[:self.write_ptr]

        return np.concatenate([part1, part2])

    # ==========================
    # 自相关 F0
    # ==========================
    def _estimate_f0(self, frame, fmin=80, fmax=400):

        frame = frame - np.mean(frame)

        energy = np.sqrt(np.mean(frame ** 2))
        if energy < 1e-4:
            return None

        autocorr = np.correlate(frame, frame, mode='full')
        autocorr = autocorr[len(autocorr) // 2:]

        min_lag = int(self.fs / fmax)
        max_lag = int(self.fs / fmin)

        if max_lag >= len(autocorr):
            return None

        lag = np.argmax(autocorr[min_lag:max_lag]) + min_lag

        return self.fs / lag

# ==============================
# 实时音频
# ==============================

fs = 16000
block_size = 1024

psola = RealtimePSOLA(fs, semitone=4)

def callback(indata, outdata, frames, time, status):
    if status:
        print(f"Status: {status}")

    try:
        input_block = indata[:, 0]
        processed = psola.process_block(input_block)
        outdata[:] = processed.reshape(-1, 1)
    except Exception as e:
        print(f"处理错误: {e}")
        # 出错时输出原始音频（安全模式）
        outdata[:] = indata


print("=" * 50)
print("PSOLA 实时变声启动")
print(f"设置: {psola.pitch_ratio:.2f} 倍音高 ({psola.pitch_ratio * 100:.0f}%)")
print("按 Ctrl+F2 停止程序...")
print("=" * 50)

try:
    with sd.Stream(
            samplerate=fs,
            blocksize=block_size,
            channels=1,
            dtype='float32',
            callback=callback):

        print("音频流已启动，正在处理...")
        print("-" * 50)

        # 添加计数器显示运行时间
        import time

        start_time = time.time()
        counter = 0

        while True:
            sd.sleep(1000)
            counter += 1
            if counter % 5 == 0:  # 每5秒显示一次状态
                elapsed = time.time() - start_time
                print(f"⏱️ 运行中... {elapsed:.0f}秒")

except KeyboardInterrupt:
    print("\n👋 检测到中断信号，正在停止程序...")

except Exception as e:
    print(f"\n❌ 发生错误: {e}")
    import traceback

    traceback.print_exc()

finally:
    print("正在清理资源...")
    print("PSOLA 实时变声已停止")
    print("=" * 50)
    sys.exit(0)