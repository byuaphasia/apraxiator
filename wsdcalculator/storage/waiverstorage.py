from datetime import datetime

from ..apraxiatorexception import NotImplementedException


class WaiverStorage:
    def is_healthy(self):
        raise NotImplementedException()

    def add_waiver(self, w):
        raise NotImplementedException()

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
        raise NotImplementedException()

    def invalidate_waiver(self, res_name, res_email):
        return self.set_waiver_validity(res_name, res_email, False)

    def update_waiver(self, res_name, res_email, date):
        raise NotImplementedException()

    def set_waiver_validity(self, res_name, res_email, validity):
        raise NotImplementedException()
