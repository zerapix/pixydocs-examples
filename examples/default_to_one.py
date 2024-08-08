# If the field isn't given a value, set it to one by default.
def default_to_one(value):
    if not value["value"]:
        return '1'
    return value
