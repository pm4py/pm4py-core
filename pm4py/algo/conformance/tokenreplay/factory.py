from pm4py import util as pmutil
from pm4py.algo.conformance.tokenreplay.versions import token_replay
from pm4py.objects.conversion.log import factory as log_converter
from pm4py.objects.log.util import general as log_util
from pm4py.objects.log.util import xes as xes_util

TOKEN_REPLAY = "token_replay"
VERSIONS = {TOKEN_REPLAY: token_replay.apply}


def apply(log, net, initial_marking, final_marking, parameters=None, variant=TOKEN_REPLAY):
    """
    Factory method to apply token-based replay
    
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
            pm4py.util.constants.PARAMETER_CONSTANT_ACTIVITY_KEY -> Activity key

    variant
        Variant of the algorithm to use
    """
    if parameters is None:
        parameters = {}
    if pmutil.constants.PARAMETER_CONSTANT_ACTIVITY_KEY not in parameters:
        parameters[pmutil.constants.PARAMETER_CONSTANT_ACTIVITY_KEY] = xes_util.DEFAULT_NAME_KEY
    if pmutil.constants.PARAMETER_CONSTANT_TIMESTAMP_KEY not in parameters:
        parameters[pmutil.constants.PARAMETER_CONSTANT_TIMESTAMP_KEY] = xes_util.DEFAULT_TIMESTAMP_KEY
    if pmutil.constants.PARAMETER_CONSTANT_CASEID_KEY not in parameters:
        parameters[pmutil.constants.PARAMETER_CONSTANT_CASEID_KEY] = log_util.CASE_ATTRIBUTE_GLUE
    return VERSIONS[variant](log_converter.apply(log, parameters, log_converter.TO_EVENT_LOG), net, initial_marking,
                             final_marking, parameters=parameters)
