class EffectChain:
    def __init__(self):
        self.effects = []

    def add_effect(self, effect):
        self.effects.append(effect)

    def process(self, audio):
        for effect in self.effects:
            audio = effect.process(audio)
        return audio
