def filter_dicts(target_dicts, key, val):
    return list(filter(lambda item: item[key] == val, target_dicts))


def find_dicts(target_dicts, key, val):
    dicts = filter_dicts(target_dicts, key, val)
    return dicts[0] if dicts else None


def find_dicts_val(target_dicts, find_key, find_val, target_key):
    item = find_dicts(target_dicts, find_key, find_val)
    return item.get(target_key) if item and isinstance(item, dict) else None
