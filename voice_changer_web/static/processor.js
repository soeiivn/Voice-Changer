class AudioProcessor extends AudioWorkletProcessor {
    constructor() {
        super();

        this.queue = [];

        this.prevSample = 0;

        // 👉 主线程传回来的音频
        this.port.onmessage = (event) => {
            this.queue.push(event.data);
        };
    }

    process(inputs, outputs) {
    const input = inputs[0];
    const output = outputs[0];

    // 🎤 采集
    if (input.length > 0) {
        const inputChannel = input[0];
        this.port.postMessage(inputChannel);
    }

    // ✅ 只取一次 chunk
    let chunk = null;
    if (this.queue.length > 0) {
        chunk = this.queue.shift();
    }

    // 🎧 播放
    for (let ch = 0; ch < output.length; ch++) {
        const out = output[ch];

        if (chunk) {
            for (let i = 0; i < out.length; i++) {
            let v = chunk ? (chunk[i] || 0) : 0;

            // ✅ 关键：简单去点击（de-click）
            v = 0.9 * v + 0.1 * this.prevSample;

            out[i] = v;
            this.prevSample = v;
            }
        } else {
            out.fill(0);
        }
    }

    return true;
}
}

registerProcessor("audio-processor", AudioProcessor);