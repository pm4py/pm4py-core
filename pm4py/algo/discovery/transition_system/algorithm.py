from pm4py import util as pmutil
from pm4py.algo.discovery.transition_system.versions import view_based
from pm4py.objects.conversion.log import converter as log_conversion
from pm4py.util import xes_constants as xes_util
from pm4py.util import exec_utils
from enum import Enum

class Variants(Enum):
    VIEW_BASED = view_based

VERSIONS = {Variants.VIEW_BASED}
VIEW_BASED = Variants.VIEW_BASED
DEFAULT_VARIANT = Variants.VIEW_BASED


def apply(log, parameters=None, variant=DEFAULT_VARIANT):
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
