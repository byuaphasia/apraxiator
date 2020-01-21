from ..apraxiatorexception import NotImplementedException

class RecordingStorage:
    def save_recording(self, recording, evaluation_id, attempt_id, owner_id):
        self._check_is_owner(evaluation_id, owner_id)
        self._save_recording(recording, attempt_id)

    def get_recording(self, evaluation_id, attempt_id, owner_id):
        self._check_is_owner(evaluation_id, owner_id)
        return self._get_recording(attempt_id)

    def _check_is_owner(self, evaluation_id, owner_id):
        raise NotImplementedException()

    def _save_recording(self, recording, attempt_id):
        raise NotImplementedException()

    def _get_recording(self, attempt_id):
        raise NotImplementedException()