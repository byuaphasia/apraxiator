from datetime import date

from ..context import src
from src.models.evaluation import Evaluation
from src.models.attempt import Attempt
from src.utils.idgenerator import IdGenerator, IdPrefix


def make_evaluation(owner_id: str, age='60', gender='male', impression='aphasia', ambiance=None) -> Evaluation:
    evaluation_id = IdGenerator.create_id(IdPrefix.EVALUATION.value)
    e = Evaluation(evaluation_id, age, gender, impression, owner_id,
                   ambiance_threshold=ambiance, date_created=date.today().isoformat())
    return e


def make_attempt(evaluation_id: str, word='gingerbread', wsd=220.5, duration=661.5, syl=3, active=True) -> Attempt:
    attempt_id = IdGenerator.create_id(IdPrefix.ATTEMPT.value)
    a = Attempt(attempt_id, evaluation_id, word, wsd, duration, syl,
                date_created=date.today().isoformat(), active=active)
    return a
