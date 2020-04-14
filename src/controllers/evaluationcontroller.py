from flask import Request
import logging

from src.services.evaluation.evaluationservice import EvaluationService
from src.apraxiatorexception import InvalidRequestException
from src.utils import read_wav, IdPrefix
from src.controllers.controllerbase import ControllerBase, authenticate_request
from src.controllers.authentication.iauthenticator import IAuthenticator


class EvaluationController(ControllerBase):
    def __init__(self, authenticator: IAuthenticator, service: EvaluationService):
        super().__init__(authenticator)
        self.service = service
        self.logger = logging.getLogger(__name__)

    @authenticate_request
    def handle_create_evaluation(self, r: Request, user: str):
        self.logger.info('[event=create-evaluation][user=%s]', user)
        age, gender, impression = self.get_create_evaluation_data(r)
        self.validate_str_field('age', age)
        self.validate_str_field('gender', gender)
        self.validate_str_field('impression', impression, length=255)
        evaluation_id = self.service.create_evaluation(user, age, gender, impression)
        return {
            'evaluationId': evaluation_id
        }

    @authenticate_request
    def handle_list_evaluations(self, r: Request, user: str):
        self.logger.info('[event=list-evaluations][user=%s]', user)
        evaluations = self.service.list_evaluations(user)
        return {
            'evaluations': sorted([e.to_list_response() for e in evaluations], key=lambda x: x['dateCreated'])
        }

    @authenticate_request
    def handle_add_ambiance(self, r: Request, user: str, evaluation_id: str):
        self.logger.info('[event=add-ambiance][user=%s][evaluationId=%s]', user, evaluation_id)
        data, sr = self.get_request_wav_file(r)
        self.validate_id(evaluation_id, IdPrefix.EVALUATION.value)
        self.service.add_ambiance(user, evaluation_id, data, sr)
        return {}

    @authenticate_request
    def handle_get_attempts(self, r: Request, user: str, evaluation_id: str):
        self.logger.info('[event=get-attempts][user=%s][evaluationId=%s]', user, evaluation_id)
        self.validate_id(evaluation_id, IdPrefix.EVALUATION.value)
        attempts = self.service.get_attempts(user, evaluation_id)
        return {
            'attempts': [a.to_response() for a in attempts]
        }

    @authenticate_request
    def handle_create_attempt(self, r: Request, user: str, evaluation_id: str):
        self.logger.info('[event=create-attempt][user=%s][evaluationId=%s]', user, evaluation_id)
        audio, sr = self.get_request_wav_file(r)
        word, syllable_count, method, save = self.get_create_attempt_data(r)
        self.validate_id(evaluation_id, IdPrefix.EVALUATION.value)
        self.validate_int_field('syllableCount', syllable_count, high=20)
        attempt_id, wsd = self.service.process_attempt(user, evaluation_id, word, syllable_count, method, audio, sr)
        if save:
            self.logger.info('[event=save-attempt-recording][user=%s][evaluationId=%s][attemptId=%s]',
                             user, evaluation_id, attempt_id)
            self.service.save_attempt_recording(user, evaluation_id, attempt_id, audio, sr)
        return {
            'attemptId': attempt_id,
            'wsd': wsd
        }

    @authenticate_request
    def handle_update_attempt(self, r: Request, user: str, evaluation_id: str, attempt_id: str):
        self.logger.info('[event=update-attempt][user=%s][evaluationId=%s][attemptId=%s]',
                         user, evaluation_id, attempt_id)
        active = self.get_update_attempt_data(r)
        self.validate_id(evaluation_id, IdPrefix.EVALUATION.value)
        self.validate_id(attempt_id, IdPrefix.ATTEMPT.value)
        self.service.update_active_status(user, evaluation_id, attempt_id, active)
        return {}

    @authenticate_request
    def handle_send_report(self, r: Request, user: str, evaluation_id: str):
        self.logger.info('[event=send-report][user=%s][evaluationId=%s]', user, evaluation_id)
        email, name = self.get_send_report_data(r)
        self.validate_str_field('email', email, length=255)
        self.validate_str_field('name', name, length=255)
        self.validate_id(evaluation_id, IdPrefix.EVALUATION.value)
        result = self.service.send_evaluation_report(user, evaluation_id, email, name)
        return result

    @staticmethod
    def validate_id(id: str, expected_prefix: str):
        if not len(id) > len(expected_prefix):
            raise InvalidRequestException(f'ID {id} is invalid, expected to be long')
        if id[0:2] != expected_prefix:
            raise InvalidRequestException(f'ID {id} is invalid, expected to start with {expected_prefix}')

    @staticmethod
    def validate_str_field(field, value, length=16):
        if not isinstance(value, str):
            raise InvalidRequestException(f'{field} is of type {type(value)}, expected a string')
        if len(value) > length:
            raise InvalidRequestException(f'{field} has length of {len(value)}, expected to be {length} or less')

    @staticmethod
    def validate_int_field(field, value, low=0, high=None):
        if low is not None and value <= low:
            raise InvalidRequestException(f'{field} is {value}, expected to be greater than {low}')
        if high is not None and value >= high:
            raise InvalidRequestException(f'{field} is {value}, expected to be less than {high}')

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
    def get_create_attempt_data(r: Request):
        syllable_count = r.values.get('syllableCount')
        word = r.values.get('word')
        if syllable_count is None:
            raise InvalidRequestException('Must provide syllable count')
        try:
            syllable_count = int(syllable_count)
        except ValueError as e:
            raise InvalidRequestException('Syllable count must be an integer', e)
        if word is None or word == '':
            raise InvalidRequestException('Must provide attempted word')

        method = r.values.get('method')
        if method is None or method == '':
            method = 'endpoint'

        save = r.values.get('save', True)
        if save == 'false' or not save:
            save = False
        else:
            save = True
        return word, syllable_count, method, save

    @staticmethod
    def get_update_attempt_data(r: Request):
        body = r.get_json(silent=True)
        if body is None:
            values = r.values
        else:
            values = body
        active = values.get('active')
        if active is None:
            raise InvalidRequestException("Only updating 'active' status is supported, must provide 'active' field")
        if active == 'false' or not active:
            active = False
        else:
            active = True
        return active

    @staticmethod
    def get_send_report_data(r: Request):
        body = r.get_json(silent=True)
        if body is None:
            values = r.values
        else:
            values = body
        try:
            email = values['email']
            name = values['name']
        except KeyError as e:
            msg = f'Must provide {e.args[0]}'
            raise InvalidRequestException(msg, e)
        return email, name

    @staticmethod
    def get_request_wav_file(r: Request):
        f = r.files.get('recording')
        if f is None:
            raise InvalidRequestException("Must provide file named 'recording'")
        return read_wav(f)
