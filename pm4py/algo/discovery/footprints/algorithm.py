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
from pm4py.algo.discovery.footprints.log.variants import entire_event_log, trace_by_trace, entire_dataframe
from pm4py.algo.discovery.footprints.petri.variants import reach_graph
from pm4py.algo.discovery.footprints.dfg.variants import dfg
from pm4py.algo.discovery.footprints.tree.variants import bottomup
from pm4py.objects.log.obj import EventLog
from pm4py.objects.petri_net.obj import PetriNet
from pm4py.objects.process_tree.obj import ProcessTree
from enum import Enum
from pm4py.util import exec_utils, pandas_utils
import pandas as pd
from typing import Optional, Dict, Any


class Variants(Enum):
    ENTIRE_EVENT_LOG = entire_event_log
    ENTIRE_DATAFRAME = entire_dataframe
    TRACE_BY_TRACE = trace_by_trace
    PETRI_REACH_GRAPH = reach_graph
    PROCESS_TREE = bottomup
    DFG = dfg


def apply(*args, variant=None, parameters: Optional[Dict[Any, Any]] = None) -> Dict[str, Any]:
    """
    Discovers a footprint object from a log/model

    Parameters
    --------------
    args
        Positional arguments that describe the log/model
    parameters
        Parameters of the algorithm
    variant
        Variant of the algorithm, including:
            - Variants.ENTIRE_EVENT_LOG
            - Variants.TRACE_BY_TRACE
            - Variants.PETRI_REACH_GRAPH
            - Variants.DFG

    Returns
    --------------
    footprints_obj
        Footprints object
    """
    if variant is None:
        if type(args[0]) is EventLog:
            variant = Variants.TRACE_BY_TRACE
        elif type(args[0]) is PetriNet:
            variant = Variants.PETRI_REACH_GRAPH
        elif type(args[0]) is ProcessTree:
            variant = Variants.PROCESS_TREE
        elif isinstance(args[0], dict):
            variant = Variants.DFG

        if pandas_utils.check_is_pandas_dataframe(args[0]):
            variant = Variants.ENTIRE_DATAFRAME

        if variant is None:
            return Exception("unsupported arguments")

    if variant in [Variants.TRACE_BY_TRACE, Variants.ENTIRE_EVENT_LOG, Variants.DFG, Variants.PROCESS_TREE,
                   Variants.ENTIRE_DATAFRAME]:
        return exec_utils.get_variant(variant).apply(args[0], parameters=parameters)
    elif variant in [Variants.PETRI_REACH_GRAPH]:
        return exec_utils.get_variant(variant).apply(args[0], args[1], parameters=parameters)
