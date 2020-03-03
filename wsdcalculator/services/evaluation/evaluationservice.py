import numpy as np

from .ievaluationstorage import IEvaluationStorage
from .calculators import WsdCalculatorBase
from ...models import Evaluation, Attempt
from ...utils import IdGenerator, IdPrefix

class EvaluationService(IdGenerator):
    def __init__(self, storage: IEvaluationStorage):
        self.storage = storage
        self.calculator = WsdCalculatorBase()

    def create_evaluation(self, user: str, age: str, gender: str, impression: str) -> str:
        evaluation_id = self.create_id(IdPrefix.EVALUATION.value)
        e = Evaluation(evaluation_id, age, gender, impression, user)
        self.storage.create_evaluation(e)
        return evaluation_id

    def list_evaluations(self, user: str):
        evaluations = self.storage.list_evaluations(user)
        return evaluations

    def add_ambiance(self, user: str, evaluation_id: str, audio, sr: int):
        self.storage.check_is_owner(user, evaluation_id)
        threshold = self.calculator.get_ambiance_threshold(audio)
        self.storage.update_evaluation(evaluation_id, 'ambiance_threshold', threshold)

    def process_attempt(self, user: str, evaluation_id: str, word: str, syllable_count: int, method: int, audio, sr: int):
        self.storage.check_is_owner(user, evaluation_id)
        evaluation = self.storage.get_evaluation(evaluation_id)
        threshold = evaluation.ambiance_threshold
        wsd, duration = self.calculator.calculate_wsd(audio, sr, syllable_count, method, threshold)
        attempt_id = self.create_id(IdPrefix.ATTEMPT.value)
        a = Attempt(attempt_id, evaluation_id, word, wsd, duration)
        self.storage.create_attempt(a)
        return attempt_id, wsd

    def update_active_status(self, user: str, evaluation_id: str, attempt_id: str, active: bool):
        self.storage.check_is_owner(user, evaluation_id)
        self.storage.update_attempt(attempt_id, 'active', active)

    def get_attempts(self, user: str, evaluation_id: str):
        self.storage.check_is_owner(user, evaluation_id)
        attempts = self.storage.get_attempts(evaluation_id)
        return attempts

    def save_attempt_recording(self, user: str, evaluation_id: str, attempt_id: str, recording):
        self.storage.check_is_owner(user, evaluation_id)
        self.storage.save_recording(attempt_id, recording)
