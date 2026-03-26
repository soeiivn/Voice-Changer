import gradio as gr
import numpy as np
from controller.engine_controller import EngineController

# =========================
# 🎯 初始化控制器
# =========================
controller = EngineController()

# =========================
# 🎯 核心处理函数
# =========================
def process_audio(audio, mode):

    if audio is None:
        return None

    sr, data = audio

    print("📥 收到音频:", data.shape, "采样率:", sr)

    # =========================
    # 1️⃣ 转单声道
    # =========================
    if len(data.shape) > 1:
        data = data.mean(axis=1)

    # =========================
    # 2️⃣ 设置音色
    # =========================
    controller.set_voice_mode(mode)

    print("🎚 当前模式:", mode)

    # =========================
    # 3️⃣ 调用 DSP
    # =========================
    processed = controller.audio_engine.process(data)

    # 防止爆音（强烈建议）
    processed = np.clip(processed, -1.0, 1.0)

    print("✅ 处理完成")

    return (sr, processed)

# =========================
# 🎯 UI 定义
# =========================
ui = gr.Interface(
    fn=process_audio,
    inputs=[
        gr.Audio(type="numpy", label="上传音频"),
        gr.Dropdown(
            ["normal", "girl", "doll", "boy", "lady", "deep", "smoky"],
            value="normal",
            label="音色选择"
        )
    ],
    outputs=gr.Audio(label="处理结果"),
    title="🎤 Voice Changer Web",
    description="上传音频，选择音色，听变声效果"
)


# =========================
# 🚀 启动
# =========================
if __name__ == "__main__":
    ui.launch()