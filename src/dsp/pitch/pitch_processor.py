import numpy as np

class PitchProcessor:

    def __init__(self, psola):
        self.psola = psola
        self.semitone = 0.0

    def set_semitone(self, semitone: float):
        self.semitone = semitone
        self.psola.set_semitone(semitone)

    def process(self, x: np.ndarray) -> np.ndarray:

        # ========= ① 输入保护 =========
        if x is None:
            print("❌ pitch 输入是 None")
            return None

        if len(x) == 0:
            print("❌ pitch 输入为空")
            return x

        # ========= ② 不变调直接返回 =========
        if self.semitone == 0:
            return x

        # ========= ③ 核心处理 =========
        try:
            y = self.psola.process_block(x)

            # ========= ④ 防止子模块炸 =========
            if y is None:
                print("❌ PSOLA 返回 None，回退原音")
                return x

            # ========= ⑤ shape保护 =========
            if len(y) != len(x):
                print("⚠️ pitch 长度变化，自动对齐")

                y = np.interp(
                    np.linspace(0, len(y) - 1, len(x)),
                    np.arange(len(y)),
                    y
                )

            return y

        except Exception as e:
            print("❌ pitch 处理异常:", e)
            return x