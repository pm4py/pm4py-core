from pm4py.algo.conformance.log_skeleton.versions import classic
from pm4py.objects.log.log import Trace
from pm4py.objects.conversion.log import converter as log_conversion
from enum import Enum
from pm4py.util import exec_utils


class Variants(Enum):
    CLASSIC = classic


CLASSIC = Variants.CLASSIC
DEFAULT_VARIANT = Variants.CLASSIC


def apply(obj, model, variant=DEFAULT_VARIANT, parameters=None):
    """
    Apply log-skeleton based conformance checking given an event log/trace
    and a log-skeleton model

    Parameters
    --------------
    obj
        Object (event log/trace)
    model
        Log-skeleton model
    variant
        Variant of the algorithm, possible values: Variants.CLASSIC
    parameters
        Parameters of the algorithm, including:
        - Parameters.ACTIVITY_KEY
        - Parameters.CONSIDERED_CONSTRAINTS, among: equivalence, always_after, always_before, never_together, directly_follows, activ_freq

    Returns
    --------------
    aligned_traces
        Conformance checking results for each trace:
        - Outputs.IS_FIT => boolean that tells if the trace is perfectly fit according to the model
        - Outputs.DEV_FITNESS => deviation based fitness (between 0 and 1; the more the trace is near to 1 the more fit is)
        - Outputs.DEVIATIONS => list of deviations in the model
    """
    if parameters is None:
        parameters = {}

    if type(obj) is Trace:
        return exec_utils.get_variant(variant).apply_trace(log_conversion.apply(obj, parameters=parameters), model,
                                                           parameters=parameters)
    else:
        return exec_utils.get_variant(variant).apply_log(log_conversion.apply(obj, parameters=parameters), model,
                                                         parameters=parameters)


def apply_from_variants_list(var_list, model, variant=DEFAULT_VARIANT, parameters=None):
    """
    Performs conformance checking using the log skeleton,
    applying it from a list of variants

    Parameters
    --------------
    var_list
        List of variants
    model
        Log skeleton model
    variant
        Variant of the algorithm, possible values: Variants.CLASSIC
    parameters
        Parameters

    Returns
    --------------
    conformance_dictio
        Dictionary containing, for each variant, the result
        of log skeleton checking
    """
    if parameters is None:
        parameters = {}

    return exec_utils.get_variant(variant).apply_from_variants_list(var_list, model, parameters=parameters)
