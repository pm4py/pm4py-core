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
from pm4py.util import exec_utils
from enum import Enum
from typing import Optional, Dict, Any, Tuple


class Parameters(Enum):
    INCLUDE_HEADER = "include_header"


def apply(temporal_profile: Dict[Tuple[str, str], Tuple[float, float]],
          parameters: Optional[Dict[Any, Any]] = None) -> str:
    """
    Abstracts a temporal profile model to a string.

    Parameters
    ----------------
    temporal_profile
        Temporal profile
    parameters
        Parameters of the method, including:
        - Parameters.INCLUDE_HEADER => includes the header in the response

    Returns
    ----------------
    text_abstr
        Textual abstraction of the log skeleton
    """
    if parameters is None:
        parameters = {}

    include_header = exec_utils.get_param_value(Parameters.INCLUDE_HEADER, parameters, True)

    ret = ["\n"]

    if include_header:
        ret.append(
            "The temporal profile is a model describing the average and the standard deviation of the times between couples of activities eventually (not only directly) following each other in at least a process execution (so in a trace <A,B,C,D> the couples (A,B) (A,C) (A,D) (B,C) (B,D) (C,D) shall be considered). Given a positive value ZETA, a deviation occurs in a process execution when the time between two activities is lower than AVG - ZETA * STDEV or greater than AVG + ZETA * STDEV. For this process, the model is:\n")

    for act_couple, agg in temporal_profile.items():
        ret.append("%s -> %s :  AVG: %.2f s  STD: %.2f s" % (act_couple[0], act_couple[1], agg[0], agg[1]))

    return "\n".join(ret)
