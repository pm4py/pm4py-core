import deprecation

from pm4py import util as pmutil
from pm4py.evaluation.generalization.versions import token_based
from pm4py.objects.conversion.log import converter as log_conversion
from pm4py.util import xes_constants as xes_util

GENERALIZATION_TOKEN = "token_replay"
VERSIONS = {GENERALIZATION_TOKEN: token_based.apply}

@deprecation.deprecated(deprecated_in='1.3.0', removed_in='2.0.0', current_version='',
                        details='Use evaluator entrypoint instead')
def apply(log, petri_net, initial_marking, final_marking, parameters=None, variant="token_replay"):
    if parameters is None:
        parameters = {}
    if pmutil.constants.PARAMETER_CONSTANT_ACTIVITY_KEY not in parameters:
        parameters[pmutil.constants.PARAMETER_CONSTANT_ACTIVITY_KEY] = xes_util.DEFAULT_NAME_KEY
    if pmutil.constants.PARAMETER_CONSTANT_TIMESTAMP_KEY not in parameters:
        parameters[pmutil.constants.PARAMETER_CONSTANT_TIMESTAMP_KEY] = xes_util.DEFAULT_TIMESTAMP_KEY
    if pmutil.constants.PARAMETER_CONSTANT_CASEID_KEY not in parameters:
        parameters[pmutil.constants.PARAMETER_CONSTANT_CASEID_KEY] = pmutil.constants.CASE_ATTRIBUTE_GLUE

    return VERSIONS[variant](log_conversion.apply(log, parameters, log_conversion.TO_EVENT_LOG), petri_net,
                             initial_marking, final_marking, parameters=parameters)
