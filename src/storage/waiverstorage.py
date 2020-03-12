from datetime import datetime

from ..apraxiatorexception import NotImplementedException
from .storageexceptions import WaiverAlreadyExists
from ..utils import TimeConversion


class WaiverStorage:
    def add_waiver(self, w):
        related_waiver = self.get_valid_waiver(w.res_email, w.res_name, w.owner_id)
        if related_waiver is not None:
            self._refresh_waiver(related_waiver.id, w.date)
            raise WaiverAlreadyExists()
        else:
            self._add_waiver(w)

    def get_valid_unexpired_waiver(self, res_email, res_name, user):
        waiver = self.get_valid_waiver(res_email, res_name, user)
        w_date = TimeConversion.from_waiver(waiver.date)
        today = datetime.now()
        diff = today - w_date
        if diff.days < 366:
            return waiver
        return None

    def get_valid_waiver(self, res_email, res_name, user):
        return None

    def invalidate_waiver(self, waiver_id, user):
        self._check_is_owner_waiver(waiver_id, user)
        self._update_waiver(waiver_id, 'valid', False)

    def _refresh_waiver(self, waiver_id, date):
        self._update_waiver(waiver_id, 'date', date)
        self._update_waiver(waiver_id, 'valid', True)

    def _check_is_owner_waiver(self, waiver_id, owner_id):
        raise NotImplementedException()

    def _update_waiver(self, waiver_id, field, value):
        raise NotImplementedException()

    def _add_waiver(self, w):
        raise NotImplementedException()
