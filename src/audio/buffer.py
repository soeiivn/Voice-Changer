import queue
import numpy as np

class AudioBuffer:
    def __init__(self, max_frames=20):
        self.q = queue.Queue(maxsize=max_frames)

    def push(self, frame: np.ndarray):
        if not self.q.full():
            self.q.put(frame.copy())

    def pop(self):
        if not self.q.empty():
            return self.q.get()
        return None
