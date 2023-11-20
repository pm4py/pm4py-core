'''
    This file is part of PM4Py (More Info: https://pm4py.fit.fraunhofer.de).

    PM4Py is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    PM4Py is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with PM4Py.  If not, see <https://www.gnu.org/licenses/>.
'''

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

    client = openai.OpenAI(api_key=api_key)

    message = {"role": "user", "content": query}

    response = client.chat.completions.create(model=model, messages=[message])

    return response.choices[0].message.content
