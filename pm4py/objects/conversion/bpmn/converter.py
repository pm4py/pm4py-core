from enum import Enum

from pm4py.objects.conversion.bpmn.variants import to_petri_net
from pm4py.util import exec_utils


class Variants(Enum):
    TO_PETRI_NET = to_petri_net


DEFAULT_VARIANT = Variants.TO_PETRI_NET


def apply(obj, variant=DEFAULT_VARIANT, parameters=None):
    if parameters is None:
        parameters = {}

    return exec_utils.get_variant(variant).apply(obj, parameters=parameters)
