from fastapi import FastAPI, UploadFile, File
from fastapi.responses import Response
from pathlib import Path
import soundfile as sf
import io
import numpy as np
import sys
ROOT_DIR = Path(__file__).resolve().parent.parent.parent

# 👉 加入 Python 路径
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

try:
    from controller.engine_controller import EngineController
    print("✅ Import success")
except ImportError as e:
    pass

# =========================
# 🎯 创建 Web 应用
# =========================
app = FastAPI()

# =========================
# 🎯 全局控制器（核心）
# =========================
controller = EngineController()

@app.post("/process_audio")
async def process_audio(file: UploadFile = File(...)):
    try:
        print("📥 收到文件:", file.filename)

        # 1️⃣ 读取
        data = await file.read()
        print("📦 文件大小:", len(data))

        # 2️⃣ 解码
        audio, sr = sf.read(io.BytesIO(data), dtype='float32')
        print("🎵 音频shape:", audio.shape, "采样率:", sr)

        # 3️⃣ 转单声道
        if len(audio.shape) > 1:
            audio = audio.mean(axis=1)
        processed = controller.audio_engine.process(audio)
        print("✅ 处理完成")

        # =========================
        # ⭐ 保存文件（关键）
        # =========================
        output_path = f"output_{file.filename}"

        sf.write(output_path, processed, sr)
        print(f"💾 已保存到: {output_path}")

        # =========================
        # 返回给浏览器（可有可无）
        # =========================
        buffer = io.BytesIO()
        sf.write(buffer, processed, sr, format='WAV')
        buffer.seek(0)

        return Response(
            content=buffer.read(),
            media_type="audio/wav"
        )
    except Exception as e:
        print("❌ 错误:", str(e))
        import traceback
        traceback.print_exc()
        return {"error": str(e)}

# =========================
# 🎯 测试接口
# =========================
@app.get("/")
def root():
    return {"msg": "Voice Changer Web Running"}

# =========================
# 🎯 设置音色
# =========================
@app.post("/set_voice")
def set_voice(mode: str):
    controller.set_voice_mode(mode)
    return {
        "status": "ok",
        "mode": mode
    }

# =========================
# 🎯 查看当前状态
# =========================
@app.get("/state")
def get_state():
    return controller.get_state()