from enum import Enum
from pm4py.util import exec_utils
from typing import Optional, Dict, Any
from pm4py.util import constants


class Parameters(Enum):
    API_KEY = "api_key"
    OPENAI_MODEL = "openai_model"


def apply(query: str, parameters: Optional[Dict[Any, Any]] = None) -> str:
    if parameters is None:
        parameters = {}

    api_key = exec_utils.get_param_value(Parameters.API_KEY, parameters, constants.OPENAI_API_KEY)
    model = exec_utils.get_param_value(Parameters.OPENAI_MODEL, parameters, constants.OPENAI_DEFAULT_MODEL)

    import openai

    openai.api_key = api_key

    messages = [{"role": "user", "content": query}]
    response = openai.ChatCompletion.create(model=model, messages=messages)
    return response["choices"][0]["message"]["content"]
