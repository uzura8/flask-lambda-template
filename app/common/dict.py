def get_striped(vals, key,  def_val=''):
    val = vals.get(key, '').strip()
    if len(val) == 0:
        val = def_val
    return val
