import inspect
import json


def jess_extension(description: str, param_descriptions: dict):
    def decorator(func):
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        param_info = {}
        required_params = []
        for param, annot in inspect.signature(func).parameters.items():
            if param == "self":
                continue
            required_params.append(param)
            param_type = "string" if annot.annotation == str else "integer"
            param_desc = param_descriptions.get(param, '')
            param_info[param] = {"type": param_type, "description": param_desc}

        wrapper._api_meta = {
            "type": "function",
            "function": {
                "name": func.__name__,
                "description": description,
                "parameters": {
                    "type": "object",
                    "properties": param_info,
                    "required": required_params
                }
            }
        }
        return wrapper
    return decorator

def get_openai_spec(func):
    return func._api_meta
