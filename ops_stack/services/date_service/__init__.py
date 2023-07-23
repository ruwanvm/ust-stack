from datetime import datetime
import pytz

usa_timezone = pytz.timezone('US/Eastern')
epoch_start = datetime(1970, 1, 1, tzinfo=pytz.utc)
default_time_format = '%Y/%m/%d %H:%M:%S.%f'


class DateTime:
    def __init__(self):
        self.usa_timezone = usa_timezone

    @staticmethod
    def to_epoch(time_string, time_format=default_time_format):
        time_raw = datetime.strptime(time_string, time_format)
        time_localized = usa_timezone.localize(time_raw)

        return int((time_localized - epoch_start).total_seconds() * 1000)

    @staticmethod
    def from_epoch(epoch, time_format=default_time_format):
        utc_time = datetime.utcfromtimestamp(epoch / 1000.0).replace(tzinfo=pytz.utc)
        time_localized = utc_time.astimezone(usa_timezone)

        return time_localized.strftime(time_format)

    @staticmethod
    def today(time_format=default_time_format):
        now = datetime.now()
        return now.astimezone(usa_timezone).strftime(time_format)
