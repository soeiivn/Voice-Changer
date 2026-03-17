import numpy as np
import sounddevice as sd
import sys
import time
import os
import pyworld as pw

class PSOLAPitchShifter:
    # ==========================
    # 六音色预设（只控制音高）
    # ==========================
    PRESETS = {
        "doll": 10,  # 娃娃音
        "girl": 6,  # 少女音
        "lady": 3,  # 御姐音
        "boy": 7,  # 正太音
        "deep": -3,  # 磁性音
        "smoky": -5,  # 烟嗓（只降音高）
    }

    def __init__(self, fs=44100, semitone=0.0):
        self.fs = fs
        self.set_semitone(semitone)

        self.fmin = 80
        self.fmax = 400

        self.f0_floor = 80
        self.f0_ceil = 400

    # ==========================
    # 设置音色（前端调用）
    # ==========================
    def set_mode(self, mode: str):
        if mode in self.PRESETS:
            self.set_semitone(self.PRESETS[mode])
            return True
        else:
            print(f"未知模式: {mode}")
            return False

    def set_semitone(self, semitone: float):
        """实时调整半音"""
        self.semitone = semitone
        self.pitch_ratio = 2 ** (semitone / 12.0)

    def _estimate_f0(self, frame: np.ndarray):
        """用 WORLD Harvest求单值 F0"""
        if len(frame) < 256:
            return None

        x = frame.astype(np.float64)
        f0, _ = pw.harvest(x, self.fs, f0_floor=self.f0_floor, f0_ceil=self.fmax)

        voiced_f0 = f0[f0 > 0]
        if len(voiced_f0) == 0:
            return None
        return np.median(voiced_f0)

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

        new_spacing = int(T / self.pitch_ratio)
        new_spacing = max(1, new_spacing)

        output = np.zeros(len(frame))
        out_ptr = 0
        mark_index = 0
        last_segment = None

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

            seg_len = len(segment)

            add_len = min(seg_len, len(output) - out_ptr)
            output[out_ptr:out_ptr + add_len] += segment[:add_len]

            last_segment = segment.copy()
            out_ptr += new_spacing
            mark_index += 1

        if out_ptr < len(output) and last_segment is not None:
            while out_ptr < len(output):
                add_len = min(len(last_segment), len(output) - out_ptr)
                output[out_ptr:out_ptr + add_len] += last_segment[:add_len]
                out_ptr += new_spacing

        output *= 0.8

        return output.reshape(input_block.shape)

# ==========================================
# 独立测试
# ==========================================
if __name__ == "__main__":

    # 测试参数
    fs = 16000  # 采样率
    block_size = 1024  # 块大小

    # 可用的音色模式列表
    available_modes = list(PSOLAPitchShifter.PRESETS.keys())

    print("=" * 60)
    print("🎵 PSOLA 六音色变声系统")
    print("=" * 60)
    print("📋 可选音色模式:")
    for i, mode in enumerate(available_modes):
        semitone = PSOLAPitchShifter.PRESETS[mode]
        semitone_str = f"+{semitone}" if semitone > 0 else str(semitone)
        print(f"   {i + 1}. {mode:6s} ({semitone_str} 半音)")
    print("-" * 60)

    # 选择模式
    while True:
        try:
            choice = input("请选择音色模式 (1-6) [默认: 2-girl]: ").strip()
            if choice == "":
                mode = "girl"
                break
            idx = int(choice) - 1
            if 0 <= idx < len(available_modes):
                mode = available_modes[idx]
                break
            else:
                print(f"❌ 请输入 1-{len(available_modes)} 之间的数字")
        except ValueError:
            print("❌ 请输入有效数字")
        except KeyboardInterrupt:
            print("\n👋 程序退出")
            sys.exit(0)

    # 创建效果器
    pitch_shifter = PSOLAPitchShifter(fs=fs)
    pitch_shifter.set_mode(mode)

    print("\n" + "=" * 60)
    print(f"🎵 PSOLA 音高变换（独立测试模式）")
    print(f"📊 参数设置:")
    print(f"   ├─ 采样率: {fs}Hz")
    print(f"   ├─ 块大小: {block_size}")
    print(f"   ├─ 音色模式: {mode}")
    print(f"   ├─ 半音数: {PSOLAPitchShifter.PRESETS[mode]:+d}")
    print(f"   └─ 音高比: {pitch_shifter.pitch_ratio:.2f}倍")
    print("=" * 60)
    print("⌨️  按 Ctrl+F2 或 Ctrl+C 停止程序")
    print("   (运行时可输入 1-6 切换音色)")
    print("-" * 60)

    # 回调函数
    def callback(indata, outdata, frames, time, status):
        if status:
            print(f"Status: {status}")

        try:
            # 处理音频
            processed = pitch_shifter.process_block(indata[:, 0])
            outdata[:] = processed.reshape(-1, 1)
        except Exception as e:
            print(f"处理错误: {e}")
            outdata[:] = indata  # 安全模式

    # 启动音频流
    try:
        with sd.Stream(
                samplerate=fs,
                blocksize=block_size,
                channels=1,
                dtype='float32',
                callback=callback
        ):
            print("▶️ 音频流已启动，正在处理...")
            print("💬 说话吧！")

            # 运行状态显示和模式切换
            counter = 0
            last_mode = mode

            while True:
                time.sleep(0.1)  # 更短的睡眠，提高响应性

                # 检查键盘输入（Windows非阻塞）
                if os.name == 'nt':  # Windows
                    import msvcrt

                    if msvcrt.kbhit():
                        key = msvcrt.getch().decode('utf-8', errors='ignore')
                        if key in '123456':
                            new_mode = available_modes[int(key) - 1]
                            if new_mode != last_mode:
                                pitch_shifter.set_mode(new_mode)
                                semitone = PSOLAPitchShifter.PRESETS[new_mode]
                                semitone_str = f"+{semitone}" if semitone > 0 else str(semitone)
                                print(f"\n🔄 切换到音色: {new_mode} ({semitone_str} 半音)")
                                last_mode = new_mode
                        elif key.lower() == 'q':
                            print("\n👋 检测到 'q' 键，正在停止程序...")
                            break

                # 每5秒显示一次状态
                counter += 1
                if counter % 50 == 0:  # 0.1 * 50 = 5秒
                    elapsed = counter / 10
                    semitone = PSOLAPitchShifter.PRESETS[last_mode]
                    semitone_str = f"+{semitone}" if semitone > 0 else str(semitone)
                    print(f"⏱️ 运行中... {elapsed:.0f}秒 [模式: {last_mode} ({semitone_str})]")

    except KeyboardInterrupt:
        print("\n👋 检测到中断信号，正在停止程序...")
    except Exception as e:
        print(f"\n❌ 运行时错误: {e}")
        import traceback

        traceback.print_exc()
    finally:
        print("\n" + "=" * 60)
        print("🏁 PSOLA 音高变换已停止")
        print("=" * 60)
        sys.exit(0)