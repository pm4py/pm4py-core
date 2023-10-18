from pm4py.algo.conformance.alignments.decomposed.variants import recompos_maximal
from enum import Enum
from pm4py.util import exec_utils
from typing import Optional, Dict, Any, Union
from pm4py.objects.log.obj import EventLog
from pm4py.objects.petri_net.obj import PetriNet, Marking
from pm4py.util import typing
import pandas as pd


class Variants(Enum):
    RECOMPOS_MAXIMAL = recompos_maximal


VERSIONS = {Variants.RECOMPOS_MAXIMAL}


def apply(log: Union[EventLog, pd.DataFrame], net: PetriNet, im: Marking, fm: Marking, variant=Variants.RECOMPOS_MAXIMAL, parameters: Optional[Dict[Any, Any]] = None) -> typing.ListAlignments:
    """
    Apply the recomposition alignment approach
    to a log and a Petri net performing decomposition

    Parameters
    --------------
    log
        Event log
    net
        Petri net
    im
        Initial marking
    fm
        Final marking
    variant
        Variant of the algorithm, possible values:
            - Variants.RECOMPOS_MAXIMAL
    parameters
        Parameters of the algorithm

    Returns
    --------------
    aligned_traces
        For each trace, return its alignment
    """
    return exec_utils.get_variant(variant).apply(log, net, im, fm, parameters=parameters)
