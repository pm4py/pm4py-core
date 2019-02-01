from pm4py import util as pmutil
from pm4py.evaluation.precision.versions import etconformance_token
from pm4py.objects.conversion.log import factory as log_conversion
from pm4py.objects.log.util import general as log_util
from pm4py.objects.log.util import xes as xes_util

ETCONFORMANCE_TOKEN = "etconformance"
VERSIONS = {ETCONFORMANCE_TOKEN: etconformance_token.apply}


def apply(log, net, marking, final_marking, parameters=None, variant=ETCONFORMANCE_TOKEN):
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
        parameters[pmutil.constants.PARAMETER_CONSTANT_CASEID_KEY] = log_util.CASE_ATTRIBUTE_GLUE

    return VERSIONS[variant](log_conversion.apply(log, parameters, log_conversion.TO_EVENT_LOG), net, marking,
                             final_marking, parameters=parameters)
