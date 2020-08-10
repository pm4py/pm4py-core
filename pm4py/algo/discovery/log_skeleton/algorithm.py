from pm4py.objects.conversion.log import converter as log_conversion
from pm4py.algo.discovery.log_skeleton.versions import classic
from enum import Enum
from pm4py.util import exec_utils


class Variants(Enum):
    CLASSIC = classic


CLASSIC = Variants.CLASSIC
DEFAULT_VARIANT = CLASSIC

VERSIONS = {CLASSIC}


def apply(log, variant=DEFAULT_VARIANT, parameters=None):
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
    return exec_utils.get_variant(variant).apply(log_conversion.apply(log, parameters=parameters), parameters=parameters)


def apply_from_variants_list(var_list, variant=DEFAULT_VARIANT, parameters=None):
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
