from pm4py.algo.simulation.playout.dfg.variants import classic
from enum import Enum
from pm4py.util import exec_utils


class Variants(Enum):
    CLASSIC = classic


def apply(dfg, start_activities, end_activities, variant=Variants.CLASSIC, parameters=None):
    """
    Applies the playout algorithm on a DFG, extracting the most likely traces according to the DFG

    Parameters
    ---------------
    dfg
        *Complete* DFG
    start_activities
        Start activities
    end_activities
        End activities
    variant
        Variant of the playout to be used, possible values:
        - Variants.CLASSIC
    parameters
        Parameters of the algorithm

    Returns
    ---------------
    simulated_log
        Simulated log
    """
    return exec_utils.get_variant(variant).apply(dfg, start_activities, end_activities, parameters=parameters)
