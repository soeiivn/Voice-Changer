import numpy as np

class EarlyReflection:
    def __init__(self, fs, verbose=False):
        self.fs = fs
        self.verbose = verbose

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

        if self.verbose:
            print(f"  ├─ 早期反射: {len(delays_ms)}条反射路径")
            for i, (d, g) in enumerate(zip(delays_ms, self.gains)):
                print(f"  │  ├─ 路径{i + 1}: {d}ms, 增益{g}")
            print(f"  └─ 最大延迟: {self.max_delay}样本 ({delays_ms[-1]}ms)")

    # ==========================
    # 主处理函数
    # ==========================
    def process(self, input_block):
        return self.process_block(input_block)

    # ==========================
    # 原处理函数（保留向后兼容）
    # ==========================
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

# ==========================================
# 独立测试
# ==========================================
if __name__ == "__main__":
    import sys
    import os
    import time

    # 获取项目根目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(current_dir))))

    # 添加项目根目录到路径
    if project_root not in sys.path:
        sys.path.insert(0, project_root)

    # 导入 AudioStream
    try:
        from Project.src.audio.stream import AudioStream
    except ImportError as e:
        print(f"❌ 导入 AudioStream 失败: {e}")
        print(f"当前 sys.path: {sys.path}")
        sys.exit(1)

    # 测试参数
    fs = 16000
    block_size = 1024

    # 创建效果器
    effect = EarlyReflection(fs, verbose=True)

    print("=" * 60)
    print("🎤 Early Reflection 早期反射（独立测试模式）")
    print(f"📊 参数设置:")
    print(f"   ├─ 采样率: {fs}Hz")
    print(f"   ├─ 块大小: {block_size}")
    print(f"   ├─ 反射路径: 7ms(0.6), 11ms(0.5), 17ms(0.4), 23ms(0.3)")
    print(f"   └─ 缓冲大小: {effect.max_delay + 1}样本")
    print("=" * 60)
    print("⌨️  按 Ctrl+f2 停止程序")
    print("-" * 60)

    # 创建音频流
    try:
        stream = AudioStream(
            fs=fs,
            block_size=block_size,
            processor=effect
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
        print("🏁 Early Reflection 早期反射已停止")
        print("=" * 60)