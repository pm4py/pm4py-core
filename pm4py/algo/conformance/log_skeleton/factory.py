from pm4py.algo.conformance.log_skeleton.versions import classic
from pm4py.objects.log.log import Trace
from pm4py.objects.conversion.log import converter as log_converter
import deprecation
import warnings

CLASSIC = "classic"

DEFAULT_VARIANT = CLASSIC

VERSIONS_LOG = {CLASSIC: classic.apply_log}
VERSIONS_TRACE = {CLASSIC: classic.apply_trace}


@deprecation.deprecated(deprecated_in='1.3.0', removed_in='2.0.0', current_version='',
                        details='Use algorithm entrypoint instead (conformance/log_skeleton/factory)')
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
        Variant of the algorithm, possible values: classic
    parameters
        Parameters of the algorithm, including:
        - the activity key (pm4py:param:activity_key)
        - the list of considered constraints (considered_constraints) among: equivalence, always_after, always_before, never_together, directly_follows, activ_freq

    Returns
    --------------
    aligned_traces
        Conformance checking results for each trace:
        - is_fit => boolean that tells if the trace is perfectly fit according to the model
        - dev_fitness => deviation based fitness (between 0 and 1; the more the trace is near to 1 the more fit is)
        - deviations => list of deviations in the model
    """
    if parameters is None:
        parameters = {}

    if type(obj) is Trace:
        return VERSIONS_TRACE[variant](log_converter.apply(obj, parameters=parameters), model, parameters=parameters)
    else:
        return VERSIONS_LOG[variant](log_converter.apply(obj, parameters=parameters), model, parameters=parameters)
