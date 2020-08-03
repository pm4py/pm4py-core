from pm4py.algo.discovery.footprints.log.variants import entire_event_log, trace_by_trace, entire_dataframe
from pm4py.algo.discovery.footprints.petri.variants import reach_graph
from pm4py.algo.discovery.footprints.dfg.variants import dfg
from pm4py.algo.discovery.footprints.tree.variants import bottomup
from pm4py.objects.log.log import EventLog
from pm4py.objects.petri.petrinet import PetriNet
from pm4py.objects.process_tree.process_tree import ProcessTree
from enum import Enum
from pm4py.util import exec_utils
from collections import Counter
import pandas as pd


class Variants(Enum):
    ENTIRE_EVENT_LOG = entire_event_log
    ENTIRE_DATAFRAME = entire_dataframe
    TRACE_BY_TRACE = trace_by_trace
    PETRI_REACH_GRAPH = reach_graph
    PROCESS_TREE = bottomup
    DFG = dfg


def apply(*args, variant=None, parameters=None):
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
        if type(args[0]) is pd.DataFrame:
            variant = Variants.ENTIRE_DATAFRAME
        elif type(args[0]) is EventLog:
            variant = Variants.TRACE_BY_TRACE
        elif type(args[0]) is PetriNet:
            variant = Variants.PETRI_REACH_GRAPH
        elif type(args[0]) is ProcessTree:
            variant = Variants.PROCESS_TREE
        elif type(args[0]) is dict or type(args[0]) is Counter:
            variant = Variants.DFG
        else:
            return Exception("unsupported arguments")

    if variant in [Variants.TRACE_BY_TRACE, Variants.ENTIRE_EVENT_LOG, Variants.DFG, Variants.PROCESS_TREE,
                   Variants.ENTIRE_DATAFRAME]:
        return exec_utils.get_variant(variant).apply(args[0], parameters=parameters)
    elif variant in [Variants.PETRI_REACH_GRAPH]:
        return exec_utils.get_variant(variant).apply(args[0], args[1], parameters=parameters)
