from pm4py.algo.conformance.alignments.dcr.variants import optimal
from enum import Enum
from pm4py.util import exec_utils
from pm4py.objects.dcr.obj import DcrGraph
from pm4py.objects.log.obj import EventLog, Trace
from typing import Optional, Dict, Any, Union, Tuple, List
from pm4py.util import typing
import pandas as pd


class Variants(Enum):
    OPTIMAL = optimal


def apply(obj: Union[EventLog, Trace], G: DcrGraph, variant=Variants.OPTIMAL, parameters: Optional[Dict[Any, Any]] = None) -> Union[typing.AlignmentResult, typing.ListAlignments]:
    """
    Applies the alignment algorithm provided a log/trace object, and a DCR graph.

    Parameters
    --------------
    obj
        Event log / Trace
    G
        DCR graph
    variant
        Variant of the DCR alignments to be used. Possible values:
        - Variants.OPTIMAL
    parameters
        Variant-specific parameters.

    Returns
    --------------
    ali
        Result of the alignment
    """
    return exec_utils.get_variant(variant).apply(obj, G, parameters=parameters)


def get_diagnostics_dataframe(log: Union[EventLog, pd.DataFrame], conf_result: List[Dict[str, Any]], variant=Variants.OPTIMAL, parameters=None) -> pd.DataFrame:
    """
    Gets the diagnostics dataframe from a log and the conformance results

    Parameters
    --------------
    log
        Event log
    conf_result
        Results of conformance checking
    variant
        Variant to be used:
        - Variants.CLASSIC
    parameters
        Variant-specific parameters

    Returns
    --------------
    diagn_dataframe
        Diagnostics dataframe
    """
    return exec_utils.get_variant(variant).get_diagnostics_dataframe(log, conf_result, parameters)