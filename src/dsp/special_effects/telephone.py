import numpy as np
from scipy.signal import butter, lfilter

# ==========================================
# Telephone Effect
# Bandpass + Soft Clipping
# ==========================================
class TelephoneEffect:
    def __init__(self, fs, verbose=False):
        self.fs = fs
        self.verbose = verbose

        # 电话带宽
        low = 300
        high = 3400

        # 归一化频率
        nyq = fs / 2

        # Butterworth 带通滤波器
        self.b, self.a = butter(
            4,
            [low / nyq, high / nyq],
            btype='band'
        )

        # 软削波阈值
        self.threshold = 0.8

        if self.verbose:
            print(f"  ├─ 电话音效: 带通 {low}-{high}Hz")
            print(f"  └─ 软削波: tanh(2x)")

    # ===============================
    # 软削波
    # ===============================
    def soft_clip(self, x):
        return np.tanh(2 * x)

    # ===============================
    # 主处理函数
    # ===============================
    def process(self, input_block):
        return self.process_block(input_block)

    # ===============================
    # 原处理函数（保留向后兼容）
    # ===============================
    def process_block(self, input_block):
        # 带通滤波
        filtered = lfilter(self.b, self.a, input_block)

        # 软削波
        distorted = self.soft_clip(filtered)

        return distorted

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
    effect = TelephoneEffect(fs, verbose=True)

    print("=" * 60)
    print("☎ Telephone Effect 电话音效（独立测试模式）")
    print(f"📊 参数设置:")
    print(f"   ├─ 采样率: {fs}Hz")
    print(f"   ├─ 块大小: {block_size}")
    print(f"   ├─ 带通滤波: 300-3400Hz")
    print(f"   └─ 软削波: tanh(2x)")
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
        print("🏁 Telephone Effect 电话音效已停止")
        print("=" * 60)