import numpy as np

# ==========================================
# Delay Echo Effect
# ==========================================
class EchoEffect:
    def __init__(self, fs, delay_ms=250, decay=0.4, verbose=False):
        self.fs = fs
        self.delay_ms = None
        self.delay_samples = 0
        self.decay = 0.0
        self.buffer = np.zeros(1)
        self.verbose = verbose

        self.ptr = 0
        self.set_params(delay_ms=delay_ms, decay=decay)

        if self.verbose:
            print(f"  ├─ 回声效果: 延迟 {delay_ms}ms ({self.delay_samples}样本)")
            print(f"  └─ 衰减系数: {decay}")

    def set_params(self, delay_ms=None, decay=None):
        if delay_ms is not None:
            self.set_delay_ms(delay_ms)

        if decay is not None:
            self.set_decay(decay)

    def set_delay_ms(self, delay_ms):
        delay_ms = float(delay_ms)
        if delay_ms <= 0:
            raise ValueError("delay_ms must be greater than 0")

        new_delay_samples = max(1, int(self.fs * delay_ms / 1000))
        if new_delay_samples != self.delay_samples:
            self.buffer = np.zeros(new_delay_samples)
            self.ptr = 0

        self.delay_ms = delay_ms
        self.delay_samples = new_delay_samples

    def set_decay(self, decay):
        decay = float(decay)
        self.decay = min(max(decay, 0.0), 0.95)

    def set_mix_ratio(self, ratio):
        self.set_decay(ratio)

    def reset(self):
        self.buffer.fill(0.0)
        self.ptr = 0

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
            # 从缓冲区读取延迟的样本
            delayed = self.buffer[self.ptr]

            # 输出 = 输入 + 衰减的延迟样本
            y = input_block[i] + self.decay * delayed

            output[i] = y

            # 写入当前样本到缓冲区
            self.buffer[self.ptr] = input_block[i]

            # 移动指针
            self.ptr += 1
            if self.ptr >= self.delay_samples:
                self.ptr = 0

        return output

# ==========================================
# 独立测试（可选）
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
    delay_ms = 300
    decay = 0.5

    # 创建效果器
    effect = EchoEffect(fs, delay_ms=delay_ms, decay=decay, verbose=True)

    print("=" * 60)
    print("🎤 Echo Effect 回声效果（独立测试模式）")
    print(f"📊 参数设置:")
    print(f"   ├─ 采样率: {fs}Hz")
    print(f"   ├─ 块大小: {block_size}")
    print(f"   ├─ 延迟时间: {delay_ms}ms ({effect.delay_samples}样本)")
    print(f"   └─ 衰减系数: {decay}")
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
        print("🏁 Echo Effect 回声效果已停止")
        print("=" * 60)