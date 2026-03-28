from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import numpy as np
import json
import os

from voice_changer_web.core.engine import AudioEngine

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = FastAPI()

# 👉 挂载静态文件
app.mount(
    "/static",
    StaticFiles(directory=os.path.join(BASE_DIR, "static")),
    name="static"
)

engine = AudioEngine(fs=16000)

@app.get("/", response_class=HTMLResponse)
async def index():
    file_path = os.path.join(BASE_DIR, "./static/index.html")

    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


# 🎧 WebSocket 音频接口
@app.websocket("/ws/audio")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    print("🎧 WebSocket connected")

    try:
        while True:
            # 🔥 支持两种消息：bytes（音频） 或 text（控制指令）
            data = await ws.receive()

            if data.get("bytes"):                     # ← 音频数据
                audio = np.frombuffer(data["bytes"], dtype=np.float32)
                processed_audio = engine.process(audio)
                await ws.send_bytes(processed_audio.astype(np.float32).tobytes())

            elif data.get("text"):                    # ← 控制指令（JSON）
                try:
                    msg = json.loads(data["text"])
                    t = msg.get("type")
                    v = msg.get("value")

                    if t == "voice_style":
                        engine.set_voice_style(v)
                    elif t == "space_effect":
                        engine.set_space_effect(v if v != "none" else None)
                    elif t == "special_effect":
                        engine.set_special_effect(v if v != "none" else None)
                    print(f"✅ 收到控制指令: {t} = {v}")
                except Exception as e:
                    print("JSON parse error:", e)
    except WebSocketDisconnect:
        print("🔌 WebSocket disconnected")