class AudioProcessor extends AudioWorkletProcessor {
    constructor() {
        super();

        this.queue = [];

        // 👉 主线程传回来的音频
        this.port.onmessage = (event) => {
            this.queue.push(event.data);
        };
    }

    process(inputs, outputs) {
        const input = inputs[0];
        const output = outputs[0];

        // 🎤 采集 → 发给主线程
        if (input.length > 0) {
            const inputChannel = input[0];
            this.port.postMessage(inputChannel);
        }

        // 🎧 播放（左右声道复制）
        for (let ch = 0; ch < output.length; ch++) {
            const out = output[ch];

            if (this.queue.length > 0) {
                const chunk = this.queue.shift();

                for (let i = 0; i < out.length; i++) {
                    out[i] = chunk[i] || 0;
                }
            } else {
                out.fill(0);
            }
        }

        return true;
    }
}

registerProcessor("audio-processor", AudioProcessor);