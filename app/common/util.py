def remove_bytes_value(values):
    '''
    TODO: for tuple and multiple list
    '''
    if not isinstance(values, (list, dict)):
        return None if isinstance(values, bytes) else values
    new_values = {}
    for key, value in values.items():
        if isinstance(value, bytes):
            continue
        new_values[key] = value
    return new_values
