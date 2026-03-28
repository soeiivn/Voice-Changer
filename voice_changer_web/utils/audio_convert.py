import numpy as np

def bytes_to_float32(data: bytes):
    return np.frombuffer(data, dtype=np.float32)

def float32_to_bytes(x: np.ndarray):
    return x.astype(np.float32).tobytes()