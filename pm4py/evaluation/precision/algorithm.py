from pm4py import util as pmutil
from pm4py.evaluation.precision.versions import etconformance_token, align_etconformance
from pm4py.objects.conversion.log import factory as log_conversion
from pm4py.util import xes_constants as xes_util
from pm4py.objects import petri


ETCONFORMANCE_TOKEN = "etconformance"
ALIGN_ETCONFORMANCE = "align_etconformance"

VERSIONS = {ETCONFORMANCE_TOKEN: etconformance_token.apply, ALIGN_ETCONFORMANCE: align_etconformance.apply}

def apply(log, net, marking, final_marking, parameters=None, variant=None):
    """
    Factory method to apply ET Conformance

    Parameters
    -----------
    log
        Trace log
    net
        Petri net
    marking
        Initial marking
    final_marking
        Final marking
    parameters
        Parameters of the algorithm, including:
            pm4py.util.constants.PARAMETER_CONSTANT_ACTIVITY_KEY -> Activity key
    variant
        Variant of the algorithm that should be applied
    """
    if parameters is None:
        parameters = {}
    if pmutil.constants.PARAMETER_CONSTANT_ACTIVITY_KEY not in parameters:
        parameters[pmutil.constants.PARAMETER_CONSTANT_ACTIVITY_KEY] = xes_util.DEFAULT_NAME_KEY
    if pmutil.constants.PARAMETER_CONSTANT_TIMESTAMP_KEY not in parameters:
        parameters[pmutil.constants.PARAMETER_CONSTANT_TIMESTAMP_KEY] = xes_util.DEFAULT_TIMESTAMP_KEY
    if pmutil.constants.PARAMETER_CONSTANT_CASEID_KEY not in parameters:
        parameters[pmutil.constants.PARAMETER_CONSTANT_CASEID_KEY] = pmutil.constants.CASE_ATTRIBUTE_GLUE

    log = log_conversion.apply(log, parameters, log_conversion.TO_EVENT_LOG)

    # execute the following part of code when the variant is not specified by the user
    if variant is None:
        if not (petri.check_soundness.check_relaxed_soundness_net_in_fin_marking(
                net,
                marking,
                final_marking)):
            # in the case the net is not a relaxed sound workflow net, we must apply token-based replay
            variant = ETCONFORMANCE_TOKEN
        else:
            # otherwise, use the align-etconformance approach (safer, in the case the model contains duplicates)
            variant = ALIGN_ETCONFORMANCE

    return VERSIONS[variant](log, net, marking,
                             final_marking, parameters=parameters)
