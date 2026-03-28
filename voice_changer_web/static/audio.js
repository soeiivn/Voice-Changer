console.log("📦 audio.js loaded (Worklet 版本)");

let ws = null;
let audioContext = null;
let stream = null;
let source = null;
let workletNode = null;

let isRunning = false;

async function startAudioProcessing(wsInstance) {
    console.log("🚀 startAudioProcessing() called");

    if (isRunning) return;
    ws = wsInstance;
    ws.binaryType = "arraybuffer";

    ws.onopen = () => { console.log("✅ WS connected"); isRunning = true; };
    ws.onclose = () => { console.log("⚠ WS closed"); isRunning = false; };
    ws.onerror = (e) => console.error("❌ WS error", e);

    // 接收后端处理完的音频并播放
    ws.onmessage = (event) => {
        if (!workletNode) return;
        const processed = new Float32Array(event.data);
        workletNode.port.postMessage(processed);
    };

    // AudioContext（必须和 engine.fs=16000 一致）
    audioContext = new (window.AudioContext || window.webkitAudioContext)({
        sampleRate: 16000
    });
    await audioContext.resume();

    // 加载 Worklet
    try {
        await audioContext.audioWorklet.addModule("/static/processor.js");
        console.log("✅ AudioWorklet loaded");
    } catch (err) {
        console.error("❌ Worklet 加载失败", err);
        return;
    }

    stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    source = audioContext.createMediaStreamSource(stream);

    workletNode = new AudioWorkletNode(audioContext, "audio-processor");

    workletNode.port.onmessage = (event) => {
        if (!isRunning || !ws || ws.readyState !== WebSocket.OPEN) return;
        ws.send(event.data.buffer);
    };

    source.connect(workletNode);
    workletNode.connect(audioContext.destination);

    console.log("🎧 Worklet pipeline ready (16000Hz)");
}

function stopAudioProcessing() {
    isRunning = false;
    if (ws) { ws.close(); ws = null; }
    if (workletNode) { workletNode.disconnect(); workletNode = null; }
    if (source) { source.disconnect(); source = null; }
    if (stream) { stream.getTracks().forEach(t => t.stop()); stream = null; }
    if (audioContext) { audioContext.close(); audioContext = null; }
    console.log("✅ stopped");
}

window.startAudioProcessing = startAudioProcessing;
window.stopAudioProcessing = stopAudioProcessing;