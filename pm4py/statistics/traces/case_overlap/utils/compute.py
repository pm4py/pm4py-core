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
from typing import Optional, Dict, Any, Tuple, List

from intervaltree import Interval, IntervalTree

from pm4py.util import exec_utils


class Parameters(Enum):
    EPSILON = "epsilon"


def apply(points: List[Tuple[float, float]], parameters: Optional[Dict[str, Any]] = None) -> List[int]:
    """
    Computes the case overlap statistic given a list of cases, expressed as (min_timestamp, max_timestamp)

    Parameters
    -----------------
    points
        List of events with the aforementioned features
    parameters
        Parameters of the method, including:
        - Parameters.EPSILON

    Returns
    -----------------
    case overlap
        List associating to each case the number of open cases during the life of a case
    """
    if parameters is None:
        parameters = {}

    epsilon = exec_utils.get_param_value(Parameters.EPSILON, parameters, 10 ** (-5))
    points = [(x[0] - epsilon, x[1] + epsilon) for x in points]
    sorted_points = sorted(points)
    tree = IntervalTree()

    for p in sorted_points:
        tree.add(Interval(p[0], p[1]))

    case_overlap = []
    for p in points:
        case_overlap.append(len(tree[p[0]:p[1]]))

    return case_overlap
