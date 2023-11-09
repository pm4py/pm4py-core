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
from pm4py.statistics.passed_time.log.variants import pre, post, prepost
from enum import Enum
from pm4py.util import exec_utils
from typing import Optional, Dict, Any
from pm4py.objects.log.obj import EventLog


class Variants(Enum):
    PRE = pre
    POST = post
    PREPOST = prepost


VERSIONS = {Variants.PRE, Variants.POST, Variants.PREPOST}


def apply(log: EventLog, activity: str, variant=Variants.PRE, parameters: Optional[Dict[Any, Any]] = None) -> Dict[str, Any]:
    """
    Gets statistics on execution times of the paths to/from the activity

    Parameters
    ------------
    log
        Log
    activity
        Activity
    variant
        Variant:
            - Variants.PRE
            - Variants.POST
            - Variants.PREPOST
    parameters
        Possible parameters of the algorithm

    Returns
    -----------
    dictio
        Dictio containing the times from/to the activity
    """
    return exec_utils.get_variant(variant).apply(log, activity, parameters=parameters)
