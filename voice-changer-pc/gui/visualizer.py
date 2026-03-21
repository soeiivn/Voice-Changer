from PyQt5.QtWidgets import QFrame, QLabel, QVBoxLayout, QWidget

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np

class VisualizerPanel(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.pipeline_label = QLabel("处理链路：等待控制器初始化。")
        self.pipeline_label.setWordWrap(True)

        # ✅ 初始化频谱图
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        self.ax = self.figure.add_subplot(111)

        self.line, = self.ax.plot(np.zeros(512))
        self.ax.set_ylim(0, 50)

        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.addWidget(self._make_summary_box())
        layout.addWidget(self.canvas)

    def update_pipeline(self, text: str):
        self.pipeline_label.setText(f"处理链路：{text}")

    # ✅ 关键：给 audio_engine 用的
    def _update_spectrum(self, spectrum):
        self.line.set_ydata(spectrum[:512])
        self.canvas.draw_idle()

    def _make_summary_box(self):
        frame = QFrame()
        layout = QVBoxLayout(frame)

        title = QLabel("核心处理链路")
        title.setStyleSheet("font-weight: bold;")

        layout.addWidget(title)
        layout.addWidget(self.pipeline_label)

        return frame