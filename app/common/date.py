import re
from datetime import datetime, timezone


def utc_iso(with_ms=False, conv_tz_spec=False, dt=None):
    if not dt:
        dt = datetime.utcnow()

    if with_ms:
        res =  dt.replace(tzinfo=timezone.utc).isoformat()
    else:
        res =  dt.replace(tzinfo=timezone.utc, microsecond=0).isoformat()

    if conv_tz_spec:
        res = res.replace('+00:00', 'Z')

    return res


def iso_offset2utc(date_offset, conv_tz_spec=False):
    date_offset_iso = re.sub('Z$','+00:00', date_offset)
    ptn = r'^(\d{4}\-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})(([\+\-])(\d{2}):(\d{2}))$'
    if not re.match(ptn, date_offset_iso):
        raise Exception('invalid')

    dt = datetime.fromisoformat(date_offset_iso)
    date_utc = dt.astimezone(tz=dt.tzinfo).astimezone(tz=timezone.utc).isoformat()
    if conv_tz_spec:
        date_utc = date_utc.replace('+00:00', 'Z')

    return date_utc


def utime2udate_iso(unixtime, conv_tz_spec=False):
    dt_utc = datetime.fromtimestamp(unixtime, timezone.utc)
    date_utc = dt_utc.isoformat()
    if conv_tz_spec:
        date_utc = date_utc.replace('+00:00', 'Z')

    return date_utc
