from pm4py.algo.conformance.tokenreplay.versions import token_replay
import pm4py
from pm4py.objects.log.util import general as log_util
from pm4py.objects.log import transform as log_transform

TOKEN_REPLAY = "token_replay"
VERSIONS = {TOKEN_REPLAY: token_replay.apply}


def apply(log, net, initial_marking, final_marking, parameters=None, variant="token_replay"):
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
    if isinstance(log, pm4py.objects.log.log.EventLog) and (not isinstance(log, pm4py.objects.log.log.TraceLog)):
        parameters = parameters if parameters is not None else dict()
        if log_util.PARAMETER_KEY_CASE_GLUE in parameters:
            glue = parameters[log_util.PARAMETER_KEY_CASE_GLUE]
        else:
            glue = log_util.CASE_ATTRIBUTE_GLUE
        if log_util.PARAMETER_KEY_CASE_ATTRIBUTE_PRFIX in parameters:
            case_pref = parameters[log_util.PARAMETER_KEY_CASE_ATTRIBUTE_PRFIX]
        else:
            case_pref = log_util.CASE_ATTRIBUTE_PREFIX
        log = log_transform.transform_event_log_to_trace_log(log, case_glue=glue,
                                                                   includes_case_attributes=False,
                                                                   case_attribute_prefix=case_pref)
    return VERSIONS[variant](log, net, initial_marking, final_marking, parameters=parameters)
