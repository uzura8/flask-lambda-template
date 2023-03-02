import re
from datetime import datetime, timezone, timedelta


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


def local_dt2udate_iso(local_dt, with_ms=False, conv_tz_spec=False):
    dt_utc = local_dt.astimezone(timezone.utc)
    return utc_iso(with_ms, conv_tz_spec, dt_utc)


def str2dt(date_str, date_format='%Y/%m/%d %H:%M:%S', ajust_to_zeropadding_fmt=False):
    if ajust_to_zeropadding_fmt:
        items = date_str.split(' ')
        y, m, d = items[0].split('/')
        date_str = '%s %s' % ('/'.join([y, m.zfill(2), d.zfill(2)]), items[1])

    return datetime.strptime(date_str, date_format)


def date_to_zfill(date_str):
    y, m, d = date_str.split('/')
    return '/'.join([y.zfill(2), m.zfill(2), d.zfill(2)])


def is_future(target_data_str, date_format='%Y-%m-%dT%H:%M:%S%z', base_date_str=None):
    target_dt = datetime.strptime(target_data_str, date_format)
    if base_date_str:
        base_dt = datetime.strptime(base_date_str, date_format)
    else:
        base_dt = datetime.now(timezone.utc)

    return target_dt > base_dt


def get_calced_date_str(base_date_str, date_format, **timedelta_args):
    if not date_format:
        date_format = '%Y-%m-%dT%H:%M:%S%z'

    if base_date_str:
        base_dt = datetime.strptime(base_date_str, date_format)
    else:
        base_dt = datetime.now(timezone.utc)

    calced_dt = base_dt + timedelta(**timedelta_args)
    return utc_iso(False, True, calced_dt)
