import numpy as np
import pyworld as pw
import sys
import sounddevice as sd
import os
import time
from src.dsp.utils.window import hann_window, apply_window
from src.dsp.utils.overlap_add import overlap_add

class PSOLAPitchShifter:

    def __init__(self, fs=44100, semitone=0.0):
        self.fs = fs
        self.set_semitone(semitone)

        self.fmin = 80
        self.fmax = 400

        self.f0_floor = 80
        self.f0_ceil = 400

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
            window = hann_window(len(segment))
            segment = apply_window(segment, window)

            add_len = min(len(segment), len(output) - out_ptr)
            overlap_add(output, segment[:add_len], out_ptr)

            last_segment = segment
            out_ptr += new_spacing
            mark_index += 1

        if out_ptr < len(output) and last_segment is not None:
            while out_ptr < len(output):
                add_len = min(len(last_segment), len(output) - out_ptr)
                output[out_ptr:out_ptr + add_len] += last_segment[:add_len]
                out_ptr += new_spacing

            # 使用固定系数而非动态归一化
        output *= 0.8

# ==========================================
# 测试代码 - 按 Ctrl+F2 退出
# ==========================================
if __name__ == "__main__":

    # 测试参数
    fs = 16000  # 采样率
    block_size = 1024  # 块大小

    # 可选的半音值
    print("=" * 60)
    print("🎵 PSOLA 音高变换测试程序")
    print("=" * 60)
    print("📋 可选半音值:")
    print("   1. +12 半音 (高八度)")
    print("   2. +6 半音 (增五度)")
    print("   3. +3 半音 (小三度)")
    print("   4. 0 半音 (原声)")
    print("   5. -3 半音 (负小三度)")
    print("   6. -5 半音 (负纯四度)")
    print("   7. -12 半音 (低八度)")
    print("-" * 60)

    # 选择半音值
    semitone_map = {
        "1": 12.0,
        "2": 6.0,
        "3": 3.0,
        "4": 0.0,
        "5": -3.0,
        "6": -5.0,
        "7": -12.0
    }

    while True:
        try:
            choice = input("请选择半音值 (1-7) [默认: 4-原声]: ").strip()
            if choice == "":
                semitone = 0.0
                break
            if choice in semitone_map:
                semitone = semitone_map[choice]
                break
            else:
                print("❌ 请输入 1-7 之间的数字")
        except KeyboardInterrupt:
            print("\n👋 程序退出")
            sys.exit(0)

    # 创建效果器
    pitch_shifter = PSOLAPitchShifter(fs=fs, semitone=semitone)

    # 显示当前设置
    semitone_str = f"+{semitone}" if semitone > 0 else str(semitone)
    print("\n" + "=" * 60)
    print(f"🎵 PSOLA 音高变换器")
    print(f"📊 参数设置:")
    print(f"   ├─ 采样率: {fs}Hz")
    print(f"   ├─ 块大小: {block_size}")
    print(f"   ├─ 半音数: {semitone_str}")
    print(f"   └─ 音高比: {pitch_shifter.pitch_ratio:.2f}倍")
    print("=" * 60)
    print("⌨️  按 Ctrl+F2 或 Ctrl+C 停止程序")
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

            # 运行状态显示
            counter = 0
            running = True

            while running:
                time.sleep(0.1)  # 更短的睡眠，提高响应性

                # 检查键盘输入（Windows非阻塞）
                if os.name == 'nt':  # Windows
                    import msvcrt
                    import ctypes

                    # 检查 Ctrl+F2 (F2 的虚拟键码是 113)
                    if msvcrt.kbhit():
                        key = msvcrt.getch()

                        # 检查是否是特殊键（以 0 或 224 开头）
                        if key == b'\x00' or key == b'\xe0':
                            second_key = msvcrt.getch()
                            # F2 在扩展键中是 \x3c
                            if second_key == b'\x3c':  # F2 键
                                print("\n🛑 检测到 Ctrl+F2，正在停止程序...")
                                running = False
                                break
                        else:
                            # 普通字符键
                            try:
                                key_char = key.decode('utf-8', errors='ignore')
                                if key_char.lower() == 'q':
                                    print("\n👋 检测到 'q' 键，正在停止程序...")
                                    running = False
                                    break
                            except:
                                pass

                else:  # Linux/Mac
                    import termios
                    import fcntl

                    try:
                        # 非阻塞键盘检测
                        fd = sys.stdin.fileno()
                        oldterm = termios.tcgetattr(fd)
                        newattr = termios.tcgetattr(fd)
                        newattr[3] = newattr[3] & ~termios.ICANON & ~termios.ECHO
                        termios.tcsetattr(fd, termios.TCSANOW, newattr)
                        oldflags = fcntl.fcntl(fd, fcntl.F_GETFL)
                        fcntl.fcntl(fd, fcntl.F_SETFL, oldflags | os.O_NONBLOCK)

                        try:
                            c = sys.stdin.read(1)
                            if c and c.lower() == 'q':
                                print("\n👋 检测到 'q' 键，正在停止程序...")
                                running = False
                                break
                        except IOError:
                            pass
                        finally:
                            termios.tcsetattr(fd, termios.TCSAFLUSH, oldterm)
                            fcntl.fcntl(fd, fcntl.F_SETFL, oldflags)
                    except:
                        # 如果上面的方法失败，使用简单的超时
                        pass

                # 每5秒显示一次状态
                counter += 1
                if counter % 50 == 0:  # 0.1 * 50 = 5秒
                    elapsed = counter / 10
                    print(f"⏱️ 运行中... {elapsed:.0f}秒 [半音: {semitone_str}]")

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