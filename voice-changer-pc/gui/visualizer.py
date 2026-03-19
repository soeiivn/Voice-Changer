from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QFrame, QLabel, QVBoxLayout, QWidget

class VisualizerPanel(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.addWidget(self._make_placeholder("输入/输出波形区域（阶段 2 接入实时数据）"))
        layout.addWidget(self._make_placeholder("频谱显示区域（阶段 3 接入 Matplotlib）"))

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