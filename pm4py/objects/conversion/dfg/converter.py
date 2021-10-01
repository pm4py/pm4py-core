from pm4py.objects.conversion.dfg.variants import to_petri_net_activity_defines_place, to_petri_net_invisibles_no_duplicates
from enum import Enum
from pm4py.util import exec_utils


class Variants(Enum):
    VERSION_TO_PETRI_NET_ACTIVITY_DEFINES_PLACE = to_petri_net_activity_defines_place
    VERSION_TO_PETRI_NET_INVISIBLES_NO_DUPLICATES = to_petri_net_invisibles_no_duplicates


DEFAULT_VARIANT = Variants.VERSION_TO_PETRI_NET_ACTIVITY_DEFINES_PLACE


def apply(dfg, parameters=None, variant=DEFAULT_VARIANT):
    return exec_utils.get_variant(variant).apply(dfg, parameters=parameters)
