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
import base64
import requests
from pm4py.util import constants


class Parameters(Enum):
    API_KEY = "api_key"
    OPENAI_MODEL = "openai_model"
    IMAGE_PATH = "image_path"


def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


def apply(prompt: str, parameters: Optional[Dict[Any, Any]] = None) -> str:
    if parameters is None:
        parameters = {}

    api_key = exec_utils.get_param_value(Parameters.API_KEY, parameters, constants.OPENAI_API_KEY)
    image_path = exec_utils.get_param_value(Parameters.IMAGE_PATH, parameters, None)
    model = exec_utils.get_param_value(Parameters.OPENAI_MODEL, parameters,
                                       constants.OPENAI_DEFAULT_MODEL if image_path is None else constants.OPENAI_DEFAULT_VISION_MODEL)

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    payload = {
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt
                    }
                ]
            }
        ]
    }

    if image_path is not None:
        base64_image = encode_image(image_path)
        payload["messages"][0]["content"].append(
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image} "}})
        payload["max_tokens"] = 4096

    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload).json()

    if "error" in response:
        # raise an exception when the request fails, with the provided message
        raise Exception(response["error"]["message"])

    return response["choices"][0]["message"]["content"]
