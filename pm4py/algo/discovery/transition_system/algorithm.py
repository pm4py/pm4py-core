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
from pm4py.algo.discovery.transition_system.variants import view_based
from pm4py.objects.conversion.log import converter as log_conversion
from pm4py.util import exec_utils
from enum import Enum
from pm4py.objects.transition_system.obj import TransitionSystem
from typing import Optional, Dict, Any, Union, Tuple
from pm4py.objects.log.obj import EventLog, EventStream
import pandas as pd


class Variants(Enum):
    VIEW_BASED = view_based

VERSIONS = {Variants.VIEW_BASED}
VIEW_BASED = Variants.VIEW_BASED
DEFAULT_VARIANT = Variants.VIEW_BASED


def apply(log: Union[EventLog, EventStream, pd.DataFrame], parameters: Optional[Dict[Any, Any]] = None, variant=DEFAULT_VARIANT) -> TransitionSystem:
    """
    Find transition system given log

    Parameters
    -----------
    log
        Log
    parameters
        Possible parameters of the algorithm, including:
            Parameters.PARAM_KEY_VIEW
            Parameters.PARAM_KEY_WINDOW
            Parameters.PARAM_KEY_DIRECTION
    variant
        Variant of the algorithm to use, including:
            Variants.VIEW_BASED

    Returns
    ----------
    ts
        Transition system
    """
    if parameters is None:
        parameters = {}

    return exec_utils.get_variant(variant).apply(log_conversion.apply(log, parameters, log_conversion.TO_EVENT_LOG), parameters=parameters)
