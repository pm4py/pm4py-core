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

from pm4py.algo.discovery.inductive.dtypes.im_ds import IMDataStructureUVCL
from pm4py.util import constants
from typing import Optional, Dict, Any, Union, Tuple


class Parameters(Enum):
    ACTIVITY_KEY = constants.PARAMETER_CONSTANT_ACTIVITY_KEY
    TIMESTAMP_KEY = constants.PARAMETER_CONSTANT_TIMESTAMP_KEY
    START_TIMESTAMP_KEY = constants.PARAMETER_CONSTANT_START_TIMESTAMP_KEY
    KEEP_FIRST_FOLLOWING = "keep_first_following"


def apply(interval_log: IMDataStructureUVCL, parameters: Optional[Dict[Union[str, Parameters], Any]] = None) -> Dict[
    Tuple[str, str], int]:
    if parameters is None:
        parameters = {}

    ret_dict = {}
    for trace, freq in interval_log.data_structure.items():
        i = 0
        while i < len(trace):
            act1 = trace[i]
            j = i + 1
            while j < len(trace):
                act2 = trace[j]
                tup = (act1, act2)
                if tup in ret_dict.keys():
                    ret_dict[tup] = ret_dict[tup] + freq
                else:
                    ret_dict[tup] = freq
                j = j + 1
            i = i + 1

    return ret_dict
