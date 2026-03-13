import numpy as np

class CombFilter:
    def __init__(self, delay, gain, verbose=False):

        self.buffer = np.zeros(delay)
        self.gain = gain
        self.ptr = 0
        self.delay = delay
        self.verbose = verbose

        if self.verbose:
            print(f"      ├─ 梳状滤波器: 延迟{delay}样本, 增益{gain}")

    def process(self, x):
        """处理单个样本"""
        y = self.buffer[self.ptr]
        self.buffer[self.ptr] = x + self.gain * y
        self.ptr = (self.ptr + 1) % len(self.buffer)
        return y

class AllpassFilter:
    def __init__(self, delay, gain, verbose=False):

        self.buffer = np.zeros(delay)
        self.gain = gain
        self.ptr = 0
        self.delay = delay
        self.verbose = verbose

        if self.verbose:
            print(f"      ├─ 全通滤波器: 延迟{delay}样本, 增益{gain}")

    def process(self, x):
        """处理单个样本"""
        buf = self.buffer[self.ptr]
        y = -x + buf
        self.buffer[self.ptr] = x + self.gain * buf
        self.ptr = (self.ptr + 1) % len(self.buffer)
        return y

class SchroederReverb:
    def __init__(self, fs, verbose=False):

        self.fs = fs
        self.verbose = verbose

        # 梳状滤波器参数
        comb_delays_ms = [29, 37, 41, 43]
        comb_gains = [0.75, 0.73, 0.71, 0.70]

        # 转换为样本数并创建梳状滤波器
        self.combs = []
        for i, (d, g) in enumerate(zip(comb_delays_ms, comb_gains)):
            delay_samples = int(fs * d / 1000)
            self.combs.append(CombFilter(delay_samples, g, verbose))

        # 全通滤波器参数
        allpass_delays_ms = [5, 1.7]
        allpass_gain = 0.7

        # 创建全通滤波器
        self.allpasses = []
        for i, d in enumerate(allpass_delays_ms):
            delay_samples = int(fs * d / 1000)
            self.allpasses.append(AllpassFilter(delay_samples, allpass_gain, verbose))

        if self.verbose:
            print(f"  ├─ Schroeder混响: {len(self.combs)}梳状 + {len(self.allpasses)}全通")
            print(f"  ├─ 梳状延迟(ms): {comb_delays_ms}")
            print(f"  ├─ 梳状增益: {comb_gains}")
            print(f"  └─ 全通延迟(ms): {allpass_delays_ms}, 增益{allpass_gain}")

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
            y = 0

            # 1. 并联梳状滤波器
            for comb in self.combs:
                y += comb.process(x)

            # 2. 平均
            y /= len(self.combs)

            # 3. 串联全通滤波器
            for ap in self.allpasses:
                y = ap.process(y)

            output[i] = y

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
    # 从 space effects 向上到 effects -> dsp -> src -> Project 根目录
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
    print("\n" + "=" * 60)
    print("🔧 初始化 Schroeder 混响效果器")
    print("=" * 60)
    effect = SchroederReverb(fs, verbose=True)

    print("\n" + "=" * 60)
    print("🎵 大厅混响效果（独立测试模式）")
    print(f"📊 参数设置:")
    print(f"   ├─ 采样率: {fs}Hz")
    print(f"   ├─ 块大小: {block_size}")
    print(f"   ├─ 梳状滤波器: 4个并联")
    print(f"   │    ├─ 延迟(ms): 29, 37, 41, 43")
    print(f"   │    └─ 增益: 0.75, 0.73, 0.71, 0.70")
    print(f"   └─ 全通滤波器: 2个串联")
    print(f"        ├─ 延迟(ms): 5, 1.7")
    print(f"        └─ 增益: 0.7, 0.7")
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
        print("🏁 Schroeder Reverb 混响效果已停止")
        print("=" * 60)