from decimal import Decimal

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


def float_to_decimal(data):
    if isinstance(data, list):
        return [float_to_decimal(item) for item in data]
    elif isinstance(data, dict):
        return {key: float_to_decimal(value) for key, value in data.items()}
    elif isinstance(data, float):
        return Decimal(str(data))
    else:
        return data
