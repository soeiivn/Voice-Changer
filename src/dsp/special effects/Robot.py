import numpy as np
from scipy.signal import butter, lfilter

# ==========================================
# Robot Voice Effect
# ==========================================
class RobotEffect:
    def __init__(self, fs, carrier_freq=200, verbose=False):
        self.fs = fs
        self.carrier_freq = carrier_freq
        self.verbose = verbose

        # 相位累加器（生成连续正弦波）
        self.phase = 0

        # 低通滤波器参数
        cutoff = 1000
        nyq = fs / 2

        self.b, self.a = butter(
            4,
            cutoff / nyq,
            btype='low'
        )

        if self.verbose:
            print(f"  ├─ 机器人音效: 载波 {carrier_freq}Hz")
            print(f"  └─ 低通滤波: {cutoff}Hz")

    # ===============================
    # 生成载波
    # ===============================
    def generate_carrier(self, length):
        t = (np.arange(length) + self.phase) / self.fs

        carrier = np.sin(2 * np.pi * self.carrier_freq * t)

        self.phase += length
        self.phase %= self.fs

        return carrier

    # ===============================
    # 主处理函数
    # ===============================
    def process(self, input_block):
        return self.process_block(input_block)

    # ===============================
    # 原处理函数（保留向后兼容）
    # ===============================
    def process_block(self, input_block):
        # 生成调制载波
        carrier = self.generate_carrier(len(input_block))

        # 环形调制
        ring_mod = input_block * carrier * 2.0

        # 低通滤波
        robot_voice = 2.0 * lfilter(self.b, self.a, ring_mod)

        return robot_voice

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
    carrier_freq = 200

    # 创建效果器
    effect = RobotEffect(fs, carrier_freq=carrier_freq, verbose=True)

    print("=" * 60)
    print("🤖 Robot Voice 机器人音效（独立测试模式）")
    print(f"📊 参数设置:")
    print(f"   ├─ 采样率: {fs}Hz")
    print(f"   ├─ 块大小: {block_size}")
    print(f"   ├─ 载波频率: {carrier_freq}Hz")
    print(f"   └─ 低通滤波: 1000Hz")
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
        print("🏁 Robot Voice 机器人音效已停止")
        print("=" * 60)