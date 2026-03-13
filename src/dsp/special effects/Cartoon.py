import numpy as np
from scipy.signal import butter, lfilter
import sounddevice as sd
import sys

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
    def process_block(self, input_block):

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
# 实时音频
# ==========================================

fs = 16000
block_size = 256

effect = CartoonEffect(fs, pitch_ratio=1.8)

def callback(indata, outdata, frames, time, status):
    if status:
        print(f"Status: {status}")

    try:
        input_block = indata[:, 0]
        processed = effect.process_block(input_block)
        outdata[:] = processed.reshape(-1, 1)
    except Exception as e:
        print(f"处理错误: {e}")
        # 出错时输出原始音频（安全模式）
        outdata[:] = indata

print("=" * 60)
print("🎭 Cartoon Effect 卡通音效启动")
print(f"音高提升: {effect.pitch_ratio}倍")
print("按 Ctrl+F2 或 Ctrl+C 停止程序")
print("=" * 60)

try:
    with sd.Stream(
            samplerate=fs,
            blocksize=block_size,
            channels=1,
            dtype='float32',
            callback=callback):

        print("▶️ 音频流已启动，正在处理...")

        while True:
            sd.sleep(1000)

except KeyboardInterrupt:
    print("\n👋 检测到中断信号，正在停止程序...")

except Exception as e:
    print(f"\n❌ 发生错误: {e}")

finally:
    print("\n" + "=" * 60)
    print("🏁 Cartoon Effect 卡通音效已停止")
    print("=" * 60)
    sys.exit(0)