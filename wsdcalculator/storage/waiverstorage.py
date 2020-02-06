from datetime import datetime

from ..apraxiatorexception import NotImplementedException
from .idgenerator import IdGenerator
from .storageexceptions import WaiverAlreadyExists, ResourceNotFoundException


class WaiverStorage(IdGenerator):
    def is_healthy(self):
        raise NotImplementedException()

    def add_waiver(self, w):
        related_waivers = self.get_valid_waivers(w.res_name, w.res_email)
        if len(related_waivers) > 0:
            prev_waiver = related_waivers[0]
            self._refresh_waiver(prev_waiver.id, w.date)
            raise WaiverAlreadyExists()
        else:
            self._add_waiver(w)

    def get_valid_unexpired_waivers(self, res_name, res_email):
        valid_waivers = self.get_valid_waivers(res_name, res_email)
        valid_unexpired_waivers = []
        for w in valid_waivers:
            w_date = datetime.strptime(w.date, '%B %d, %Y')
            today = datetime.now()
            diff = today - w_date
            if diff.days < 366:
                valid_unexpired_waivers.append(w)
        return valid_unexpired_waivers

    def get_valid_waivers(self, res_name, res_email):
        return []

    def invalidate_waiver(self, res_name, res_email):
        related_waivers = self.get_valid_unexpired_waivers(res_name, res_email)
        if len(related_waivers) == 0:
            raise ResourceNotFoundException('waiver')
        for w in related_waivers:
            self._update_waiver(w.id, 'valid', False)

    def _refresh_waiver(self, waiver_id, date):
        self._update_waiver(waiver_id, 'date', date)
        self._update_waiver(waiver_id, 'valid', True)

    def _update_waiver(self, waiver_id, field, value):
        raise NotImplementedException()

    def _add_waiver(self, w):
        raise NotImplementedException()
