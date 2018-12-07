import json

def serialize_to_dict(obj : object) -> dict:
    """ Serialize Object to Dictionary Recursively
    
    Arguments:
        obj {object} --  string, list, or dictionary to be serialize
    
    Returns:
        dict -- Serialized Dictionary
    """
    return to_dict(obj)

def to_dict(obj : object) -> dict:
    """ Serialize Object to Dictionary Recursively
    
    Arguments:
        obj {object} --  string, list, or dictionary to be serialize
    
    Returns:
        dict -- Serialized Dictionary
    """
    
    if isinstance(obj, dict):
        data = {}
        for k, v in obj.items():
            data[k] = to_dict(v)
        return data
        
    elif hasattr(obj, "_ast"):
        return to_dict(obj._ast())
        
    elif hasattr(obj, "__iter__") and not isinstance(obj, str):
        return [to_dict(v) for v in obj]
        
    elif hasattr(obj, "__dict__"):
        data = {key : to_dict(value) for key, value in obj.__dict__.items() if not callable(value) and not key.startswith('_')}
        
    elif isinstance(obj, str):
        try:
            data = {}
            obj = json.loads(obj)
            for k, v in obj.items():
                data[k] = to_dict(v)
                return data
        except:
            return obj

    else:
        return obj