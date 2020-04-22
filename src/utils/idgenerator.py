import uuid
from enum import Enum


class IdGenerator:
    @staticmethod
    def create_id(prefix):
        id_format = '{}-{}'
        return id_format.format(prefix, str(uuid.uuid4()))


class IdPrefix(Enum):
    EVALUATION = 'EV'
    ATTEMPT = 'AT'
    WAIVER = 'WV'
