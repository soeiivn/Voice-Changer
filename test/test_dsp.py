import numpy as np
import pytest

try:
    from src.engine.processor import AudioProcessor
except ImportError:
    pass

# =========================
# 🎯 基础测试信号
# =========================
def generate_sine(freq=440, sr=16000, duration=1.0):
    t = np.linspace(0, duration, int(sr * duration), endpoint=False)
    return 0.1 * np.sin(2 * np.pi * freq * t).astype(np.float32)


# =========================
# 🎯 音高变换测试（PSOLA）
# =========================
def test_pitch_shift():
    processor = AudioProcessor()
    processor.set_voice_mode("girl")

    x = generate_sine()
    y = processor.process_block(x)

    assert len(y) == len(x)
    assert not np.allclose(x, y)


# =========================
# 🎯 空间效果测试（Echo）
# =========================
def test_echo_effect():
    processor = AudioProcessor()
    processor.set_space_effect("echo")

    x = generate_sine()
    y = processor.process_block(x)

    assert len(y) == len(x)
    assert np.max(np.abs(y)) >= np.max(np.abs(x))


# =========================
# 🎯 混响测试
# =========================
def test_reverb_effect():
    processor = AudioProcessor()
    processor.set_space_effect("reverb")

    x = generate_sine()
    y = processor.process_block(x)

    assert len(y) == len(x)


# =========================
# 🎯 特殊效果测试（Robot）
# =========================
def test_robot_effect():
    processor = AudioProcessor()
    processor.set_special_effect("robot")

    x = generate_sine()
    y = processor.process_block(x)

    assert len(y) == len(x)
    assert not np.allclose(x, y)


# =========================
# 🎯 多效果叠加测试
# =========================
def test_combined_effects():
    processor = AudioProcessor()

    processor.set_voice_mode("girl")
    processor.set_space_effect("echo")

    x = generate_sine()
    y = processor.process_block(x)

    assert len(y) == len(x)


# =========================
# 🎯 边界测试（空输入）
# =========================
def test_empty_input():
    processor = AudioProcessor()

    x = np.array([], dtype=np.float32)
    y = processor.process_block(x)

    assert len(y) == 0