document.addEventListener('DOMContentLoaded', () => {
  const wsUrl = `ws://${location.host}/ws/audio`;
  let ws = new WebSocket(wsUrl);

  // UI 元素
  const voiceSelect = document.getElementById('voice_style');
  const spaceSelect = document.getElementById('space_effect');
  const specialSelect = document.getElementById('special_effect');
  const startBtn = document.getElementById('start_btn');
  const stopBtn = document.getElementById('stop_btn');

  // 发送控制指令
  function sendControl(type, value) {
    if (ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify({ type, value }));
    }
  }

  // 绑定下拉框
  voiceSelect.addEventListener('change', () => sendControl('voice_style', voiceSelect.value));
  spaceSelect.addEventListener('change', () => sendControl('space_effect', spaceSelect.value));
  specialSelect.addEventListener('change', () => sendControl('special_effect', specialSelect.value));

  // Start / Stop
  startBtn.addEventListener('click', () => {
    startBtn.classList.add('hidden');
    stopBtn.classList.remove('hidden');
    window.startAudioProcessing(ws);   // 调用 audio.js 的函数
  });

  stopBtn.addEventListener('click', () => {
    stopBtn.classList.add('hidden');
    startBtn.classList.remove('hidden');
    window.stopAudioProcessing();
  });

  // WebSocket 重连
  ws.onclose = () => {
    console.log('WS 断开，3秒后重连...');
    setTimeout(() => { ws = new WebSocket(wsUrl); }, 3000);
  };
});