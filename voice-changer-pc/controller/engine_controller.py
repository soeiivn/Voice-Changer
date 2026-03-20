from dataclasses import asdict, dataclass

from PyQt5.QtCore import QObject, pyqtSignal

@dataclass
class ProcessingState:
    """State mirrored between the UI and the future audio engine."""
    running: bool = False
    voice_mode: str = "normal"
    space_effect: str = "none"
    special_effect: str = "none"
    pitch_semitone: int = 0
    echo_ratio: float = 0.4

class EngineController(QObject):

    state_changed = pyqtSignal(dict)
    status_changed = pyqtSignal(str)
    pipeline_changed = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.state = ProcessingState()
        self._emit_full_state("阶段 2：控制器已接入，等待启动音频引擎。")

    def start(self):
        self.state.running = True
        self._emit_full_state("控制器状态：已启动，下一阶段接入真实音频流。")

    def stop(self):
        self.state.running = False
        self._emit_full_state("控制器状态：已停止。")

    def set_voice_mode(self, mode: str):
        self.state.voice_mode = mode
        self._emit_full_state()

    def set_space_effect(self, effect: str):
        self.state.space_effect = effect
        self._emit_full_state()

    def set_special_effect(self, effect: str):
        self.state.special_effect = effect
        self._emit_full_state()

    def set_pitch_semitone(self, value: int):
        self.state.pitch_semitone = int(value)
        self._emit_full_state()

    def set_echo_ratio_from_percent(self, value: int):
        self.state.echo_ratio = max(0.0, min(value / 100.0, 0.95))
        self._emit_full_state()

    def get_state(self) -> dict:
        return asdict(self.state)

    def build_pipeline_summary(self) -> str:
        chain = ["输入语音"]

        if self.state.voice_mode != "normal" or self.state.pitch_semitone != 0:
            chain.append(f"音高模块[{self.state.voice_mode}, {self.state.pitch_semitone:+d}]")

        if self.state.space_effect != "none":
            if self.state.space_effect == "echo":
                chain.append(f"空间模块[echo, ratio={self.state.echo_ratio:.2f}]")
            else:
                chain.append(f"空间模块[{self.state.space_effect}]")

        if self.state.special_effect != "none":
            chain.append(f"特殊模块[{self.state.special_effect}]")

        chain.append("输出语音")
        return " → ".join(chain)

    def _emit_full_state(self, status_message=None):
        state_dict = self.get_state()
        self.state_changed.emit(state_dict)
        self.pipeline_changed.emit(self.build_pipeline_summary())

        if status_message is None:
            status_message = (
                f"当前配置：音色={self.state.voice_mode} | 空间={self.state.space_effect} | "
                f"特效={self.state.special_effect} | 音高={self.state.pitch_semitone:+d} | "
                f"回声比例={self.state.echo_ratio:.2f}"
            )

        self.status_changed.emit(status_message)