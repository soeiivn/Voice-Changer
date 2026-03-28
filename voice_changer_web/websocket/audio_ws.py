from fastapi import WebSocket, FastAPI
import numpy as np
from voice_changer_web.core.engine import AudioEngine

app = FastAPI()
engine = AudioEngine(fs=16000)

@app.websocket("/ws/audio")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    print("🎧 WebSocket connected")

    try:
        while True:
            data = await ws.receive_bytes()

            audio = np.frombuffer(data, dtype=np.float32)

            processed = engine.process(audio)

            await ws.send_bytes(processed.tobytes())

    except Exception as e:
        print("❌ WS error:", e)