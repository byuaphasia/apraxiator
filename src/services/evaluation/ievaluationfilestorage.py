class IEvaluationFileStorage:
    def save_recording(self, attempt_id: str, audio, sr: int):
        raise NotImplementedError()
