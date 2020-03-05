from ...models import Evaluation, Attempt


class IEvaluationStorage:
    def check_is_owner(self, user: str, evaluation_id: str):
        raise NotImplementedError()

    def create_evaluation(self, e: Evaluation):
        raise NotImplementedError()

    def list_evaluations(self, user: str):
        raise NotImplementedError()

    def update_evaluation(self, evaluation_id: str, field: str, value):
        raise NotImplementedError()

    def get_evaluation(self, evaluation_id):
        raise NotImplementedError()

    def create_attempt(self, a: Attempt):
        raise NotImplementedError()

    def update_attempt(self, attempt_id: str, field: str, value):
        raise NotImplementedError()

    def get_attempts(self, evaluation_id: str):
        raise NotImplementedError()

    def save_recording(self, attempt_id: str, recording):
        raise NotImplementedError()
