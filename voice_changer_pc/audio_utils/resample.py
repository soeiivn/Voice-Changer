import numpy as np
from scipy.signal import resample

def resample_audio(audio: np.ndarray, src_rate: int, target_rate: int) -> np.ndarray:
    """通用重采样（支持任意采样率）"""
    if src_rate == target_rate:
        return audio.astype(np.float32)

    duration = len(audio) / src_rate
    target_length = int(round(duration * target_rate))
    resampled = resample(audio, target_length)
    return resampled.astype(np.float32)


# 专用快捷函数
def downsample_48k_to_16k(audio: np.ndarray):
    return resample_audio(audio, 48000, 16000)


def upsample_16k_to_48k(audio: np.ndarray):
    return resample_audio(audio, 16000, 48000)