from voice_changer_web.utils.audio_convert import *

class AudioProcessor:
    def __init__(self, controller):
        self.controller = controller

    def process_bytes(self, data: bytes) -> bytes:
        x = bytes_to_float32(data)
        y = self.controller.process(x)
        return float32_to_bytes(y)