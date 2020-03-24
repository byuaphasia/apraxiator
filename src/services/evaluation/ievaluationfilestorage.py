class IEvaluationFileStorage:
    def save_recording(self, attempt_id: str, recording):
        raise NotImplementedError()
