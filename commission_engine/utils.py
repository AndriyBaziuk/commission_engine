from calendar import monthrange
from datetime import datetime


def get_days_in_month() -> int:
    today = datetime.today()
    return monthrange(today.year, today.month)[1]
