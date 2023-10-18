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
