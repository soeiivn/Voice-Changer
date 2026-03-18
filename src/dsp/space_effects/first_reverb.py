import numpy as np

class FDNReverb:
    def __init__(self, fs, verbose=False):

        self.fs = fs
        self.verbose = verbose

        # 延迟时间(ms) - 使用质数避免周期叠加
        delays_ms = [13, 17, 19, 23]

        # 反馈系数
        self.gains = [0.55, 0.52, 0.50, 0.48]

        # 转换为采样点
        self.delays = [int(fs * d / 1000) for d in delays_ms]

        # 创建延迟缓冲区
        self.buffers = [np.zeros(d) for d in self.delays]

        # 指针数组
        self.ptrs = [0] * len(self.delays)

        if self.verbose:
            print(f"  ├─ FDN混响: {len(delays_ms)}条延迟线")
            for i, (d, g) in enumerate(zip(delays_ms, self.gains)):
                print(f"  │  ├─ 路径{i + 1}: {d}ms, 增益{g}")
            print(f"  └─ 最大延迟: {max(delays_ms)}ms")

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

        for n in range(len(input_block)):
            x = input_block[n]
            y_total = 0

            # 并行处理所有延迟线
            for i in range(len(self.buffers)):
                buffer = self.buffers[i]
                ptr = self.ptrs[i]
                gain = self.gains[i]

                # 读取延迟样本
                delayed = buffer[ptr]

                # 反馈计算
                y = x + gain * delayed

                # 写入反馈
                buffer[ptr] = y

                # 移动指针
                self.ptrs[i] = (ptr + 1) % len(buffer)

                # 累加输出
                y_total += delayed

            # 平均输出
            output[n] = y_total / len(self.buffers)

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

    # 创建效果器
    effect = FDNReverb(fs, verbose=True)

    print("=" * 60)
    print("🎵 FDN Reverb 混响效果（独立测试模式）")
    print(f"📊 参数设置:")
    print(f"   ├─ 采样率: {fs}Hz")
    print(f"   ├─ 块大小: {block_size}")
    print(f"   ├─ 延迟时间(ms): 13, 17, 19, 23")
    print(f"   ├─ 反馈系数: 0.55, 0.52, 0.50, 0.48")
    print(f"   └─ 缓冲总数: {len(effect.buffers)}条延迟线")
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
        print("🏁 FDN Reverb 混响效果已停止")
        print("=" * 60)