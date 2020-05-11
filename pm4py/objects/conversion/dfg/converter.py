from pm4py.objects.conversion.dfg.versions import to_petri_net_activity_defines_place
from enum import Enum
from pm4py.util import exec_utils


class Variants(Enum):
    VERSION_TO_PETRI_NET_ACTIVITY_DEFINES_PLACE = to_petri_net_activity_defines_place


DEFAULT_VARIANT = Variants.VERSION_TO_PETRI_NET_ACTIVITY_DEFINES_PLACE


def apply(dfg, parameters=None, variant=DEFAULT_VARIANT):
    return exec_utils.get_variant(variant).apply(dfg, parameters=parameters)
