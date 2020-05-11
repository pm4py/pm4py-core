from pm4py.algo.conformance.tokenreplay.versions import token_replay, backwards
from pm4py.objects.conversion.log import converter as log_converter
from enum import Enum
from pm4py.util import exec_utils

class Variants(Enum):
    TOKEN_REPLAY = token_replay
    BACKWARDS = backwards

VERSIONS = {Variants.TOKEN_REPLAY, Variants.BACKWARDS}
DEFAULT_VARIANT = Variants.TOKEN_REPLAY


def apply(log, net, initial_marking, final_marking, parameters=None, variant=DEFAULT_VARIANT):
    """
    Method to apply token-based replay
    
    Parameters
    -----------
    log
        Log
    net
        Petri net
    initial_marking
        Initial marking
    final_marking
        Final marking
    parameters
        Parameters of the algorithm, including:
            Parameters.ACTIVITY_KEY -> Activity key
    variant
        Variant of the algorithm to use:
            - Variants.TOKEN_REPLAY
            - Variants.BACKWARDS
    """
    if parameters is None:
        parameters = {}
    return exec_utils.get_variant(variant).apply(log_converter.apply(log, parameters, log_converter.TO_EVENT_LOG), net, initial_marking,
                             final_marking, parameters=parameters)
