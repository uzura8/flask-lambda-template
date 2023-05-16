def get_striped(vals, key,  def_val=''):
    val = vals.get(key, '').strip()
    if len(val) == 0:
        val = def_val
    return val


def keys_from_dicts(dicts, key):
    tmp = {}
    for i in dicts:
        k = i[key]
        tmp[k] = 1
    return list(tmp.keys())
