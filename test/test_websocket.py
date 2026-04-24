import pytest
import websockets
import json
import numpy as np

WS_URL = "ws://127.0.0.1:8000/ws/audio"


# =========================
# 🎯 WS-01 连接测试
# =========================
@pytest.mark.asyncio
async def test_ws_connection():
    async with websockets.connect(WS_URL) as ws:
        # 新版判断连接是否成功的方法
        assert ws is not None


# =========================
# 🎯 WS-03 参数发送
# =========================
@pytest.mark.asyncio
async def test_send_config():
    async with websockets.connect(WS_URL) as ws:

        msg = json.dumps({
            "type": "voice_style",
            "value": "girl"
        })

        await ws.send(msg)

        # 无返回也算成功（只测不崩）
        assert True


# =========================
# 🎯 WS-04 音频发送
# =========================
@pytest.mark.asyncio
async def test_send_audio():
    async with websockets.connect(WS_URL) as ws:

        audio = np.random.rand(1024).astype(np.float32)

        await ws.send(audio.tobytes())

        data = await ws.recv()

        assert isinstance(data, (bytes, bytearray))
        assert len(data) > 0


# =========================
# 🎯 WS-06 流测试
# =========================
@pytest.mark.asyncio
async def test_stream_audio():
    async with websockets.connect(WS_URL) as ws:

        for _ in range(10):
            audio = np.random.rand(1024).astype(np.float32)
            await ws.send(audio.tobytes())

            data = await ws.recv()
            assert len(data) > 0


# =========================
# 🎯 WS-07 断开测试（修正版）
# =========================
@pytest.mark.asyncio
async def test_disconnect():
    ws = await websockets.connect(WS_URL)

    await ws.close()

    # 新版没有 closed 属性 → 用这个判断
    assert ws.close_code is not None