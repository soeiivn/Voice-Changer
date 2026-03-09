import time
import numpy as np
import sounddevice as sd

class EarlyReflection:

    def __init__(self, fs):

        self.fs = fs

        # 反射时间 (ms)
        delays_ms = [7, 11, 17, 23]

        # 衰减系数
        self.gains = [0.6, 0.5, 0.4, 0.3]

        # 转换为采样点
        self.delays = [int(fs * d / 1000) for d in delays_ms]

        self.max_delay = max(self.delays)

        # 延迟缓冲
        self.buffer = np.zeros(self.max_delay + 1)

        self.ptr = 0

    def process_block(self, input_block):

        output = np.zeros_like(input_block)

        for i in range(len(input_block)):

            x = input_block[i]

            y = x

            # 多路径反射
            for delay, gain in zip(self.delays, self.gains):
                read_ptr = (self.ptr - delay) % len(self.buffer)

                y += gain * self.buffer[read_ptr]

            output[i] = y

            # 写入当前样本
            self.buffer[self.ptr] = x

            # 移动指针
            self.ptr = (self.ptr + 1) % len(self.buffer)

        return output


fs = 16000
block_size = 1024
early_reflect = EarlyReflection(fs)


def callback(indata, outdata, frames, time, status):
    if status:
        print(f"Status: {status}")
    input_block = indata[:, 0]
    processed = early_reflect.process_block(input_block)
    outdata[:, 0] = processed

print("🎤 Early Reflection Start")
print("按 Ctrl+F2 停止程序...")
print("=" * 40)

try:
    # 创建并启动音频流
    stream = sd.Stream(
        samplerate=fs,
        blocksize=block_size,
        channels=1,
        dtype='float32',
        callback=callback
    )

    with stream:
        print("音频流已启动，正在处理...")

        # 无限循环，直到被中断
        while True:
            time.sleep(0.1)  # 短暂睡眠，让CPU可以响应中断

except KeyboardInterrupt:
    # 捕获 Ctrl+F2
    print("\n👋 检测到中断信号，正在停止程序...")

except Exception as e:
    print(f"\n❌ 发生错误: {e}")

finally:
    # 确保资源被释放
    print("正在关闭音频流...")
    if 'stream' in locals():
        stream.stop()
        stream.close()
    print("程序已停止")