import numpy as np
from Project.src.dsp.utils.f0 import estimate_f0
from Project.src.dsp.utils.window import hann_window, apply_window
from Project.src.dsp.utils.overlap_add import overlap_add

class RealtimePSOLA:

    def __init__(self, fs, semitone=0, verbose=False):
        self.fs = fs
        self.semitone = semitone
        self.pitch_ratio = 2 ** (semitone / 12)
        self.verbose = verbose

        # 分析缓冲
        self.buffer_size = 4096
        self.buffer = np.zeros(self.buffer_size)
        self.write_ptr = 0

        # 上次周期
        self.prev_f0 = 150
        self.T = int(fs / self.prev_f0)

        if self.verbose:
            print(f"  ├─ PSOLA音高变换: {self.pitch_ratio:.2f}倍 ({semitone}半音)")

    # ==========================
    # 主处理函数
    # ==========================
    def process(self, input_block):
        return self.process_block(input_block)

    # ==========================
    # 原处理函数（保留向后兼容）
    # ==========================
    def process_block(self, input_block):

        N = len(input_block)

        # 写入环形缓冲
        for i in range(N):
            self.buffer[self.write_ptr] = input_block[i]
            self.write_ptr = (self.write_ptr + 1) % self.buffer_size

        frame = self._get_recent_frame(2048)

        f0 = estimate_f0(frame, self.fs)

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

            window = hann_window(len(segment))
            segment = apply_window(segment, window)

            seg_len = len(segment)

            if out_ptr + seg_len > N:
                break

            success = overlap_add(output, segment, out_ptr)

            if not success:
                break

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

# ==========================================
# 独立测试
# ==========================================
if __name__ == "__main__":
    import sys
    import os
    import time

    # 获取项目根目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))

    # 添加项目根目录到路径
    if project_root not in sys.path:
        sys.path.insert(0, project_root)

    # 导入 AudioStream
    try:
        from src.audio.stream import AudioStream
    except ImportError as e:
        print(f"❌ 导入 AudioStream 失败: {e}")
        print(f"当前 sys.path: {sys.path}")
        sys.exit(1)

    # 测试参数
    fs = 16000
    block_size = 1024
    semitone = 4  # 升高4半音

    # 创建效果器
    effect = RealtimePSOLA(fs, semitone=semitone, verbose=True)

    print("=" * 60)
    print("🎵 PSOLA 音高变换（独立测试模式）")
    print(f"📊 参数设置:")
    print(f"   ├─ 采样率: {fs}Hz")
    print(f"   ├─ 块大小: {block_size}")
    print(f"   ├─ 半音数: {semitone}")
    print(f"   └─ 音高比: {effect.pitch_ratio:.2f}倍")
    print("=" * 60)
    print("⌨️  按 Ctrl+f2 停止程序")
    print("-" * 60)

    # 创建音频流
    try:
        stream = AudioStream(
            fs=fs,
            block_size=block_size,
            processor=effect  # effect 现在有 process 方法
        )
    except Exception as e:
        print(f"❌ 创建音频流失败: {e}")
        sys.exit(1)

    try:
        print("▶️ 音频流已启动，正在处理...")
        stream.start()

        counter = 0
        while True:
            time.sleep(1)
            counter += 1
            if counter % 5 == 0:
                print(f"⏱️ 运行中... {counter}秒")

    except KeyboardInterrupt:
        print("\n👋 检测到中断信号，正在停止程序...")
    except Exception as e:
        print(f"\n❌ 运行时错误: {e}")
    finally:
        print("\n" + "=" * 60)
        print("🏁 PSOLA 音高变换已停止")
        print("=" * 60)