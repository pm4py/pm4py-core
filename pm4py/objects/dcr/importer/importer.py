from enum import Enum

from pm4py.objects.dcr.importer.variants import dcrxml, json, discover
from pm4py.util import exec_utils


class Variants(Enum):
    DCRXML = dcrxml
    JSON = json
    DISCOVER = discover


DEFAULT_VARIANT = Variants.DCRXML


def apply(path, variant=DEFAULT_VARIANT, parameters=None):
    if parameters is None:
        parameters = {}

    return exec_utils.get_variant(variant).apply(path, parameters=parameters)


def deserialize(dcr_string, variant=DEFAULT_VARIANT, parameters=None):
    if parameters is None:
        parameters = {}

    return exec_utils.get_variant(variant).import_from_string(dcr_string, parameters=parameters)
