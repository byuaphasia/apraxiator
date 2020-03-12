from ...models import Waiver


class IWaiverStorage:

    def get_valid_waiver(self, user: str, subject_name: str, subject_email: str):
        raise NotImplementedError()

    def check_is_owner_waiver(self, user: str, waiver_id: str):
        raise NotImplementedError()

    def update_waiver(self, waiver_id: str, field: str, value):
        raise NotImplementedError()

    def add_waiver_to_storage(self, w: Waiver):
        raise NotImplementedError()
