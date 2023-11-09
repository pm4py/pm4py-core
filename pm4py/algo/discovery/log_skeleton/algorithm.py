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
from pm4py.algo.discovery.log_skeleton.variants import classic
from enum import Enum
from pm4py.util import exec_utils
from typing import Optional, Dict, Any, Union, Tuple, List
from pm4py.objects.log.obj import EventLog, EventStream
import pandas as pd


class Variants(Enum):
    CLASSIC = classic


CLASSIC = Variants.CLASSIC
DEFAULT_VARIANT = CLASSIC

VERSIONS = {CLASSIC}


def apply(log: Union[EventLog, EventStream, pd.DataFrame], variant=DEFAULT_VARIANT, parameters: Optional[Dict[Any, Any]] = None) -> Dict[str, Any]:
    """
    Discover a log skeleton from an event log

    Parameters
    -------------
    log
        Event log
    variant
        Variant of the algorithm, possible values:
        - Variants.CLASSIC
    parameters
        Parameters of the algorithm, including:
            - the activity key (Parameters.ACTIVITY_KEY)
            - the noise threshold (Parameters.NOISE_THRESHOLD)

    Returns
    -------------
    model
        Log skeleton model
    """
    return exec_utils.get_variant(variant).apply(log, parameters=parameters)


def apply_from_variants_list(var_list: List[Tuple[str, int]], variant=DEFAULT_VARIANT, parameters: Optional[Dict[Any, Any]] = None) -> Dict[str, Any]:
    """
    Discovers the log skeleton from the variants list

    Parameters
    ---------------
    var_list
        Variants list
    variant
        Variant of the algorithm, possible values:
        - Variants.CLASSIC
    parameters
        Parameters

    Returns
    -------------
    model
        Log skeleton model
    """
    return exec_utils.get_variant(variant).apply_from_variants_list(var_list, parameters=parameters)
