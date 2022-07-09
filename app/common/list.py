def filter_dicts(target_dicts, key, val):
    return list(filter(lambda item: item[key] == val, target_dicts))


def find_dicts(target_dicts, key, val):
    dicts = filter_dicts(target_dicts, key, val)
    return dicts[0] if dicts else None
