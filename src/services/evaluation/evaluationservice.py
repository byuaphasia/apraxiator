import os

from .ievaluationstorage import IEvaluationStorage
from .ievaluationfilestorage import IEvaluationFileStorage
from .calculators import WsdCalculatorBase
from ...models import Evaluation, Attempt
from ...utils import IdGenerator, IdPrefix, ISender, PDFGenerator


class EvaluationService(IdGenerator):
    def __init__(self, storage: IEvaluationStorage, file_store: IEvaluationFileStorage,
                 email_sender: ISender, pdf_generator: PDFGenerator):
        self.storage = storage
        self.file_store = file_store
        self.calculator = WsdCalculatorBase()
        self.email_sender = email_sender
        self.pdf_generator = pdf_generator

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
        a = Attempt(attempt_id, evaluation_id, word, wsd, duration, syllable_count)
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
        self.file_store.save_recording(attempt_id, recording)

    def send_evaluation_report(self, user: str, evaluation_id: str, email: str, name: str):
        self.storage.check_is_owner(user, evaluation_id)
        attempts, evaluation = self.get_evaluation_report(evaluation_id)
        report_file = self.pdf_generator.generate_report(evaluation, attempts, name)
        self.email_sender.send_report(report_file, email, evaluation_id)
        if os.path.exists(report_file):
            os.remove(report_file)
        return {
            'attempts': attempts,
            'evaluation': evaluation
        }

    def get_evaluation_report(self, evaluation_id: str):
        unfiltered = self.storage.get_attempts(evaluation_id)
        attempts = []
        for a in unfiltered:
            if a.active:
                attempts.append(a.to_report())
        evaluation = self.storage.get_evaluation(evaluation_id).to_report()
        return attempts, evaluation
