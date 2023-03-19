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
from pm4py.algo.transformation.log_to_target.variants import next_activity, next_time, remaining_time
from pm4py.objects.log.obj import EventLog, EventStream
import pandas as pd
from typing import Union, Dict, Optional, Any, Tuple, List
from pm4py.util import exec_utils


class Variants(Enum):
    NEXT_ACTIVITY = next_activity
    NEXT_TIME = next_time
    REMAINING_TIME = remaining_time


def apply(log: Union[EventLog, EventStream, pd.DataFrame], variant=None, parameters: Optional[Dict[Any, Any]] = None) -> Tuple[Any, List[str]]:
    """
    Extracts from the event log
    the target vector for a specific ML use case

    Parameters
    ---------------
    log
        Event log / Event stream / Pandas dataframe
    variant
        Specification of the target vector:
        - Variants.NEXT_ACTIVITY => encodes the next activity
        - Variants.NEXT_TIME => encodes the next timestamp
        - Variants.REMAINING_TIME => encodes the remaining time

    Returns
    --------------
    vector
        Target vector for the specified ML use case
    classes
        Classes (for every column of the target vector)
    """
    if variant is None:
        raise Exception("please provide the variant between: Variants.NEXT_ACTIVITY, Variants.NEXT_TIME, Variants.REMAINING_TIME")
    return exec_utils.get_variant(variant).apply(log, parameters=parameters)
