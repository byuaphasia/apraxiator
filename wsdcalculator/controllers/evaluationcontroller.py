from flask import Request
import logging

from ..services import EvaluationService
from ..apraxiatorexception import InvalidRequestException

class EvaluationController:
    def __init__(self, service: EvaluationService):
        self.service = service
        self.logger = logging.getLogger(__name__)

    def handle_create_evaluation(self, r: Request, user: str):
        self.logger.info('[event=create-evaluation][user=%s]', user)
        age, gender, impression = self.get_create_evaluation_data(r)
        self.validate_str_field('age', age)
        self.validate_str_field('gender', gender)
        self.validate_str_field('impression', impression, length=255)
        return self.service.create_evaluation(age, gender, impression, user)

    def handle_add_ambiance(self, r: Request, user: str, evaluation_id: str):
        self.logger.info('[event=add-ambiance][user=%s][evaluationId=%s]', user, evaluation_id)
        age, gender, impression = self.get_request_data(r)
        self.validate_str_field('age', age)
        self.validate_str_field('gender', gender)
        self.validate_str_field('impression', impression, length=255)
        return self.service.create_evaluation(age, gender, impression, user)

    @staticmethod
    def validate_str_field(field, value, length=16):
        if not isinstance(value, str):
            raise InvalidRequestException(f'{field} is of type {type(value)}, expected a boolean')
        if len(value) > length:
            raise InvalidRequestException(f'{field} has length of {len(value)}, expected to be {length} or less')

    @staticmethod
    def get_create_evaluation_data(r: Request):
        body = r.get_json(silent=True)
        if body is None:
            # If no/bad json body, pull values from request form or query params
            values = r.values
        else:
            values = body

        try:
            age = values['age']
            gender = values['gender']
            impression = values['impression']
        except KeyError as e:
            msg = f'Must provide {e.args[0]}'
            raise InvalidRequestException(msg, e)

        return age, gender, impression

    @staticmethod
    def get_add_ambiance_data(r: Request):
        f = r.files['recording']