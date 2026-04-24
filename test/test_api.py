import websockets
import json
import pytest
import numpy as np
import asyncio
asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

URI = "ws://127.0.0.1:8000/ws/audio"


# =========================
# 生成假音频（模拟麦克风）
# =========================
def generate_audio_block():
    return np.random.randn(1024).astype(float).tolist()


# =========================
# 测试1：连接测试
# =========================
@pytest.mark.asyncio
async def test_connection():
    async with websockets.connect(URI) as ws:
        print("✅ WebSocket connected successfully")


# =========================
# 测试2：发送配置
# =========================
@pytest.mark.asyncio
async def test_send_config():
    async with websockets.connect(URI) as ws:

        config = {
            "voice": "girl",
            "space": "echo",
            "special": "robot",
            "echo_ratio": 0.5,
            "echo_delay": 120
        }

        await ws.send(json.dumps(config))
        print("✅ Config sent")

        # 尝试接收（如果后端有返回）
        try:
            msg = await asyncio.wait_for(ws.recv(), timeout=2)
            print("📩 Received:", msg)
        except:
            print("ℹ️ No response (正常情况)")


# =========================
# 测试3：发送音频流
# =========================
@pytest.mark.asyncio
async def test_stream_audio():
    async with websockets.connect(URI) as ws:

        # 先发配置
        await ws.send(json.dumps({"voice": "girl"}))

        # 连续发送音频
        for i in range(5):
            audio_block = generate_audio_block()
            await ws.send(json.dumps({"audio": audio_block}))
            print(f"🎤 Sent audio block {i}")

            # 尝试接收处理结果
            try:
                msg = await asyncio.wait_for(ws.recv(), timeout=1)
                print("📩 Received audio chunk")
            except:
                print("ℹ️ No return (可能是单向流)")


# =========================
# 运行所有测试
# =========================
async def main():
    print("\n=== Test 1: Connection ===")
    await test_connection()

    print("\n=== Test 2: Config ===")
    await test_send_config()

    print("\n=== Test 3: Streaming ===")
    await test_stream_audio()


if __name__ == "__main__":
    asyncio.run(main())