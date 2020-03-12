from datetime import datetime


class TimeConversion:
    @staticmethod
    def from_waiver(date: str):
        return datetime.strptime(date, '%B %d, %Y')

    @staticmethod
    def to_report(date: datetime):
        if date is None:
            date = datetime.now()
        return date.strftime('%B %d, %Y')
