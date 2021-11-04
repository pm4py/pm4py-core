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
from typing import Optional, Dict, Any, List, Union

import pandas as pd

from pm4py.statistics.overlap.utils import compute
from pm4py.util import constants, xes_constants, exec_utils


class Parameters(Enum):
    START_TIMESTAMP_KEY = constants.PARAMETER_CONSTANT_START_TIMESTAMP_KEY
    TIMESTAMP_KEY = constants.PARAMETER_CONSTANT_TIMESTAMP_KEY


def apply(df: pd.DataFrame, parameters: Optional[Dict[Union[str, Parameters], Any]] = None) -> List[int]:
    """
    Counts the intersections of each interval event with the other interval events of the log
    (all the events are considered, not looking at the activity)

    Parameters
    ----------------
    df
        Pandas dataframe
    parameters
        Parameters of the algorithm, including:
        - Parameters.START_TIMESTAMP_KEY => the attribute to consider as start timestamp
        - Parameters.TIMESTAMP_KEY => the attribute to consider as timestamp

    Returns
    -----------------
    overlap
        For each interval event, ordered by the order of appearance in the log, associates the number
        of intersecting events.
    """
    if parameters is None:
        parameters = {}

    start_timestamp_key = exec_utils.get_param_value(Parameters.START_TIMESTAMP_KEY, parameters,
                                                     xes_constants.DEFAULT_TIMESTAMP_KEY)
    timestamp_key = exec_utils.get_param_value(Parameters.TIMESTAMP_KEY, parameters,
                                               xes_constants.DEFAULT_TIMESTAMP_KEY)

    df = df[{start_timestamp_key, timestamp_key}].to_dict('records')
    points = []

    for event in df:
        points.append((event[start_timestamp_key].timestamp(), event[timestamp_key].timestamp()))

    return compute.apply(points)
