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
from pm4py.algo.discovery.correlation_mining.variants import classic_split, classic, trace_based
from pm4py.util import exec_utils
from enum import Enum
from typing import Optional, Dict, Any, Union, Tuple
from pm4py.objects.log.obj import EventLog, EventStream
import pandas as pd


class Variants(Enum):
    CLASSIC_SPLIT = classic_split
    CLASSIC = classic
    TRACE_BASED = trace_based


DEFAULT_VARIANT = Variants.CLASSIC


def apply(log: Union[EventLog, EventStream, pd.DataFrame], variant=DEFAULT_VARIANT, parameters: Optional[Dict[Any, Any]] = None) -> Tuple[Dict[Tuple[str, str], int], Dict[Tuple[str, str], float]]:
    """
    Applies the Correlation Miner to the event stream (a log is converted to a stream)

    The approach is described in:
    Pourmirza, Shaya, Remco Dijkman, and Paul Grefen. "Correlation miner: mining business process models and event
    correlations without case identifiers." International Journal of Cooperative Information Systems 26.02 (2017):
    1742002.

    Parameters
    -------------
    log
        Log object
    variant
        Variant of the algorithm to use
    parameters
        Parameters of the algorithm

    Returns
    --------------
    dfg
        Directly-follows graph
    performance_dfg
        Performance DFG (containing the estimated performance for the arcs)
    """
    if parameters is None:
        parameters = {}

    return exec_utils.get_variant(variant).apply(log, parameters=parameters)
