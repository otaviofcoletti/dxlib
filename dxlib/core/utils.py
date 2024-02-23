def serialize(obj: any):
    if isinstance(obj, (str, int, float)):
        return obj
    elif isinstance(obj, dict):
        return {serialize(key): serialize(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [serialize(item) for item in obj]
    elif isinstance(obj, tuple):
        return tuple([serialize(item) for item in obj])
    elif hasattr(obj, "to_dict"):
        return serialize(obj.to_dict())
    return obj


def deserialize(obj: any):
    if isinstance(obj, (str, int, float)):
        return obj
    elif isinstance(obj, dict):
        return {deserialize(key): deserialize(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [deserialize(item) for item in obj]
    elif isinstance(obj, tuple):
        return tuple([deserialize(item) for item in obj])
    return obj
