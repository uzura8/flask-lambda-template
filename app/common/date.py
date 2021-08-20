import datetime

def utc_iso(with_ms=False, conv_tz_spec=False, dt=None):
    if not dt:
        dt = datetime.datetime.utcnow()

    if with_ms:
        res =  dt.replace(tzinfo=datetime.timezone.utc).isoformat()
    else:
        res =  dt.replace(tzinfo=datetime.timezone.utc, microsecond=0).isoformat()

    if conv_tz_spec:
        res = res.replace('+00:00', 'Z')

    return res
