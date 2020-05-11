from pm4py.evaluation.generalization.versions import token_based
from pm4py.objects.conversion.log import converter as log_conversion
from enum import Enum
from pm4py.util import exec_utils


class Variants(Enum):
    GENERALIZATION_TOKEN = token_based


GENERALIZATION_TOKEN = Variants.GENERALIZATION_TOKEN
VERSIONS = {GENERALIZATION_TOKEN}


def apply(log, petri_net, initial_marking, final_marking, parameters=None, variant=GENERALIZATION_TOKEN):
    if parameters is None:
        parameters = {}

    return exec_utils.get_variant(variant).apply(log_conversion.apply(log, parameters, log_conversion.TO_EVENT_LOG),
                                                 petri_net,
                                                 initial_marking, final_marking, parameters=parameters)
