import numpy as np
from scipy.signal import butter, lfilter

class CartoonEffect:

    def __init__(self, fs, pitch_ratio=1.8):
        self.fs = fs
        self.pitch_ratio = pitch_ratio

        cutoff = 800
        nyq = fs / 2

        self.b, self.a = butter(2, cutoff / nyq, btype='high')

    # ==========================
    # Pitch shift (resample)
    # ==========================
    def pitch_shift(self, x):

        N = len(x)

        if not hasattr(self, "idx") or len(self.idx) != N:
            self.idx = np.arange(0, N, self.pitch_ratio)

        idx = self.idx
        idx = idx[idx < N]

        shifted = np.interp(idx, np.arange(N), x)

        if len(shifted) < N:
            shifted = np.pad(shifted, (0, N - len(shifted)))

        return shifted[:N]

    # ==========================
    # Soft clipping
    # ==========================
    def soft_clip(self, x, drive=1.2):
        return np.tanh(2.0 * drive * x)

    # ==========================
    # 主处理
    # ==========================
    def process(self, input_block):

        x = input_block.copy()

        # ==========================
        # 防止过载（归一化）
        # ==========================
        peak = np.max(np.abs(x))
        if peak > 0.7:
            x = x / peak * 0.7

        # 1 升调
        pitch_up = self.pitch_shift(x)

        # 2 高频增强
        filtered = lfilter(self.b, self.a, pitch_up)

        # 3 波形整形
        cartoon = self.soft_clip(filtered)

        cartoon *= 0.5

        return cartoon

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
    block_size = 256

    # 创建效果器
    effect = CartoonEffect(fs, pitch_ratio=1.8)

    print("=" * 60)
    print("🎭 Cartoon Effect 卡通音效启动（独立测试模式）")
    print(f"📊 参数设置:")
    print(f"   ├─ 采样率: {fs}Hz")
    print(f"   ├─ 块大小: {block_size}")
    print(f"   ├─ 音高提升: {effect.pitch_ratio}倍")
    print(f"   ├─ 高通滤波: 800Hz")
    print(f"   └─ 软削波: tanh(2.4x)")
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
        print("🏁 Cartoon Effect 卡通音效已停止")
        print("=" * 60)