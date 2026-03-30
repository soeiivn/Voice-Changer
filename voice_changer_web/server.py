from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import numpy as np
import json
import os
from pathlib import Path

from voice_changer_web.core.engine import AudioEngine

BASE_DIR = Path(__file__).resolve().parent          # ← 指向 voice_changer_web/
STATIC_DIR = BASE_DIR / "static"

app = FastAPI(title="Voice Changer Pro")

# 静态文件（你的路径现在完全正确）
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

engine = AudioEngine(fs=16000)

# ==================== 页面路由 ====================
@app.get("/", response_class=HTMLResponse)
async def homepage():
    return (STATIC_DIR / "homepage.html").read_text(encoding="utf-8")

@app.get("/app", response_class=HTMLResponse)
async def app_page():
    return (STATIC_DIR / "index.html").read_text(encoding="utf-8")   # 你原来的 index.html 作为工作室

@app.get("/about", response_class=HTMLResponse)
async def about_page():
    return (STATIC_DIR / "about.html").read_text(encoding="utf-8")

# ==================== WebSocket（你原来的音频逻辑，完全不动）===================
@app.websocket("/ws/audio")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    print("🎧 WebSocket connected")

    try:
        while True:
            data = await ws.receive()
            if data.get("bytes"):                     # 音频
                audio = np.frombuffer(data["bytes"], dtype=np.float32)
                processed_audio = engine.process(audio)
                await ws.send_bytes(processed_audio.astype(np.float32).tobytes())

            elif data.get("text"):                    # 控制指令
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
                    elif t == "pitch":
                        engine.set_pitch(v)
                    elif t == "formant":
                        engine.set_formant(v)
                    elif t == "echo_ratio":
                        engine.set_echo_ratio(v)
                    print(f"✅ 收到控制指令: {t} = {v}")
                except Exception as e:
                    print("JSON parse error:", e)
    except WebSocketDisconnect:
        print("🔌 WebSocket disconnected")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=9000)