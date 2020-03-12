from flask import Request
import logging

from ..services import WaiverService
from ..apraxiatorexception import InvalidRequestException
from ..utils import TimeConversion, IdPrefix
from .authentication import IAuthenticator
from .controllerbase import ControllerBase, authenticate_request


class WaiverController(ControllerBase):
    def __init__(self, authenticator: IAuthenticator, service: WaiverService):
        super().__init__(authenticator)
        self.service = service
        self.logger = logging.getLogger(__name__)

    @authenticate_request
    def handle_save_subject_waiver(self, r: Request, user: str):
        self.logger.info('[event=save-subject-waiver][user=%s]', user)
        subject_name, subject_email, clinician_email, date_signed = self.get_save_subject_waiver_data(r)
        subject_signature_file = self.get_request_subject_signature_file(r)
        self.validate_str_field('subjectName', subject_name)
        self.validate_str_field('subjectEmail', subject_email)
        self.validate_str_field('clinicianEmail', clinician_email)
        self.validate_date_format(date_signed)
        self.service.save_subject_waiver(user, subject_name, subject_email, clinician_email, date_signed, subject_signature_file)
        return {}

    @authenticate_request
    def handle_save_representative_waiver(self, r: Request, user: str):
        self.logger.info('[event=save-representative-waiver][user=%s]', user)
        subject_name, subject_email, clinician_email, date_signed, representative_name, relationship = self.get_save_representative_waiver_data(r)
        representative_signature_file = self.get_request_representative_signature_file(r)
        self.validate_str_field('subjectName', subject_name)
        self.validate_str_field('subjectEmail', subject_email)
        self.validate_str_field('clinicianEmail', clinician_email)
        self.validate_date_format(date_signed)
        self.validate_str_field('representativeName', representative_name)
        self.validate_str_field('relationship', relationship)
        self.service.save_representative_waiver(user, subject_name, subject_email, clinician_email, date_signed, representative_name, relationship, representative_signature_file)
        return {}

    @authenticate_request
    def handle_invalidate_waiver(self, r: Request, user: str, waiver_id: str):
        self.logger.info('[event=invalidate-waiver][user=%s]', user)
        self.validate_id(waiver_id)
        self.service.invalidate_waiver(user, waiver_id)
        return {}

    @authenticate_request
    def handle_check_waivers(self, r: Request, user: str):
        self.logger.info('[event=check-waivers][user=%s]', user)
        subject_name, subject_email = self.get_check_waivers_data(r)
        self.validate_str_field('subjectName', subject_name)
        self.validate_str_field('subjectEmail', subject_email)
        result = self.service.check_waivers(user, subject_name, subject_email)
        return result

    @staticmethod
    def get_save_subject_waiver_data(r: Request):
        body = r.get_json(silent=True)
        if body is None:
            # If no/bad json body, pull values from request form or query params
            values = r.values
        else:
            values = body

        try:
            subject_name = values['subjectName']
            subject_email = values['subjectEmail']
            clinician_email = values['clinicianEmail']
            date_signed = values['dateSigned']
        except KeyError as e:
            msg = f'Must provide {e.args[0]}'
            raise InvalidRequestException(msg, e)

        return subject_name, subject_email, clinician_email, date_signed

    @staticmethod
    def get_save_representative_waiver_data(r: Request):
        body = r.get_json(silent=True)
        if body is None:
            # If no/bad json body, pull values from request form or query params
            values = r.values
        else:
            values = body

        try:
            subject_name = values['subjectName']
            subject_email = values['subjectEmail']
            clinician_email = values['clinicianEmail']
            date_signed = values['dateSigned']
            representative_name = values['representativeName']
            relationship = values['relationship']
        except KeyError as e:
            msg = f'Must provide {e.args[0]}'
            raise InvalidRequestException(msg, e)

        return subject_name, subject_email, clinician_email, date_signed, representative_name, relationship

    @staticmethod
    def get_check_waivers_data(r: Request):
        body = r.get_json(silent=True)
        if body is None:
            # If no/bad json body, pull values from request form or query params
            values = r.values
        else:
            values = body

        try:
            subject_name = values['subjectName']
            subject_email = values['subjectEmail']
        except KeyError as e:
            msg = f'Must provide {e.args[0]}'
            raise InvalidRequestException(msg, e)

        return subject_name, subject_email

    @staticmethod
    def validate_id(id: str):
        if not len(id) > len(IdPrefix.WAIVER.value):
            raise InvalidRequestException(f'ID {id} is invalid, expected to be long')
        if id[0:2] != IdPrefix.WAIVER.value:
            raise InvalidRequestException(f'ID {id} is invalid, expected to start with {IdPrefix.WAIVER.value}')

    @staticmethod
    def validate_date_format(date_str: str):
        try:
            TimeConversion.from_waiver(date_str)
        except Exception as e:
            raise InvalidRequestException('Incorrect date format, expected \'MMMM DD, YYYY\'', e)

    @staticmethod
    def get_request_subject_signature_file(r: Request):
        f = r.files.get('subjectSignature')
        if f is None:
            raise InvalidRequestException('Must provide file named \'subjectSignature\'')
        return f

    @staticmethod
    def get_request_representative_signature_file(r: Request):
        f = r.files.get('representativeSignature')
        if f is None:
            raise InvalidRequestException('Must provide file named \'representativeSignature\'')
        return f

    @staticmethod
    def validate_str_field(field: str, value, length=255):
        if not isinstance(value, str):
            raise InvalidRequestException(f'{field} is of type {type(value)}, expected a string')
        if len(value) > length:
            raise InvalidRequestException(f'{field} has length of {len(value)}, expected to be {length} or less')
