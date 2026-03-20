from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QFrame, QLabel, QVBoxLayout, QWidget

class VisualizerPanel(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.pipeline_label = QLabel("处理链路：等待控制器初始化。")
        self.pipeline_label.setWordWrap(True)
        self.pipeline_label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.addWidget(self._make_summary_box())
        layout.addWidget(self._make_placeholder("输入/输出波形区域（阶段 2 接入实时数据）"))
        layout.addWidget(self._make_placeholder("频谱显示区域（阶段 3 接入 Matplotlib）"))

    def update_pipeline(self, pipeline_text: str):
        self.pipeline_label.setText(f"处理链路：{pipeline_text}")

    def _make_summary_box(self) -> QWidget:
        frame = QFrame()
        frame.setFrameShape(QFrame.StyledPanel)
        frame_layout = QVBoxLayout(frame)
        title = QLabel("核心处理链路")
        title.setStyleSheet("font-weight: bold;")
        frame_layout.addWidget(title)
        frame_layout.addWidget(self.pipeline_label)
        return frame

    @staticmethod
    def _make_placeholder(title: str) -> QWidget:
        frame = QFrame()
        frame.setFrameShape(QFrame.StyledPanel)
        frame.setMinimumHeight(180)
        frame_layout = QVBoxLayout(frame)

        label = QLabel(title)
        label.setAlignment(Qt.AlignCenter)
        label.setWordWrap(True)
        frame_layout.addStretch(1)
        frame_layout.addWidget(label)
        frame_layout.addStretch(1)

        return frame