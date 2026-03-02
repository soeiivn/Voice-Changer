import sounddevice as sd
import numpy as np
import threading
from Project.src.audio.buffer import AudioBuffer
from Project.src.audio.effects.chain import EffectChain
from effects.gain import Gain

effect_chain = EffectChain()
gain = Gain(2.0)
effect_chain.add_effect(gain)

audio_buffer = AudioBuffer(max_frames=10)

SAMPLE_RATE = 16000
BLOCK_SIZE = 512
CHANNELS = 1

# ========= 运行控制标志 =========
running = True

def audio_callback(indata, outdata, frames, time, status):
    if status:
        print(status)

    audio = indata.copy()
    processed = effect_chain.process(audio)
    processed = np.clip(processed, -1.0, 1.0)
    outdata[:] = processed

def wait_for_stop():
    """
    阻塞等待用户输入，用于优雅停止音频流
    """
    global running
    input("Press ENTER to stop audio...\n")
    running = False

def run():
    global running

    # 启动一个线程监听“停止指令”
    stop_thread = threading.Thread(target=wait_for_stop, daemon=True)
    stop_thread.start()

    try:
        with sd.Stream(
            samplerate=SAMPLE_RATE,
            blocksize=BLOCK_SIZE,
            channels=CHANNELS,
            dtype='float32',
            callback=audio_callback
        ):
            print("Real-time audio passthrough running...")
            print("Speak into the microphone.")

            while running:
                sd.sleep(100)

    except KeyboardInterrupt:
        print("\nKeyboard interrupt received.")

    finally:
        running = False
        print("Audio stream stopped cleanly.")

if __name__ == "__main__":
    run()
