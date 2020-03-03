import uuid

class IdGenerator:
    id_format = '{}-{}'
    def create_id(self, prefix):
        id = self.id_format.format(prefix, str(uuid.uuid4()))
        return id