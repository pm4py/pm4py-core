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
from pm4py.util import exec_utils, xes_constants
import pandas as pd
from typing import Optional, Dict, Any, Union, Tuple


class Parameters(Enum):
    ACTIVITY_KEY = "activity_key"
    RETURN_MAPPING = "return_mapping"


def apply(dataframe: pd.DataFrame, parameters: Optional[Dict[Any, Any]] = None) -> Union[
    pd.DataFrame, Tuple[pd.DataFrame, Dict[str, str]]]:
    """
    Remap the activities in a dataframe using an augmented alphabet to minimize the size of the encoding

    Running example:

        import pm4py
        from pm4py.objects.log.util import activities_to_alphabet
        from pm4py.util import constants

        dataframe = pm4py.read_xes("tests/input_data/running-example.xes")
        renamed_dataframe = activities_to_alphabet.apply(dataframe, parameters={constants.PARAMETER_CONSTANT_ACTIVITY_KEY: "concept:name"})
        print(renamed_dataframe)

    Parameters
    --------------
    dataframe
        Pandas dataframe
    parameters
        Parameters of the method, including:
        - Parameters.ACTIVITY_KEY => attribute to be used as activity
        - Parameters.RETURN_MAPPING => (boolean) enables the returning the mapping dictionary (so the original activities can be re-constructed)

    Returns
    --------------
    ren_dataframe
        Pandas dataframe in which the activities have been remapped to the (augmented) alphabet
    inv_mapping
        (if required) Dictionary associating to every letter of the (augmented) alphabet the original activity
    """
    if parameters is None:
        parameters = {}

    activity_key = exec_utils.get_param_value(Parameters.ACTIVITY_KEY, parameters, xes_constants.DEFAULT_NAME_KEY)
    return_mapping = exec_utils.get_param_value(Parameters.RETURN_MAPPING, parameters, False)

    activities_count = list(dataframe[activity_key].value_counts().to_dict())
    remap_dict = {}
    for index, act in enumerate(activities_count):
        result = ''
        while index >= 0:
            result = chr((index % 26) + ord('A')) + result
            index = index // 26 - 1
        remap_dict[act] = result
    dataframe[activity_key] = dataframe[activity_key].map(remap_dict)
    if return_mapping:
        inverse_dct = {y: x for x, y in remap_dict.items()}
        return dataframe, inverse_dct
    return dataframe
