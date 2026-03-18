class AudioRouting:
    def __init__(self, processor):
        self.processor = processor

    # =========================
    # 🎯 重置（非常重要）
    # =========================
    def reset(self):
        self.processor.enable_pitch = False
        self.processor.enable_space = None
        self.processor.enable_special = None

    # =========================
    # 🎯 设置音色
    # =========================
    def set_voice(self, mode):
        self.processor.set_voice_mode(mode)

    # =========================
    # 🎯 设置空间效果
    # =========================
    def set_space(self, effect):
        self.processor.enable_space = effect

    # =========================
    # 🎯 设置特殊效果
    # =========================
    def set_special(self, effect):
        self.processor.enable_special = effect

    # =========================
    # 🎯 一键组合（核心）
    # =========================
    def apply_config(self, config: dict):

        self.reset()

        if config.get("voice"):
            self.set_voice(config["voice"])

        if config.get("space"):
            self.set_space(config["space"])

        if config.get("special"):
            self.set_special(config["special"])