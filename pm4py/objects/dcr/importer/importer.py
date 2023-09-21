from enum import Enum

from pm4py.objects.dcr.importer.variants import xml_dcr_portal
from pm4py.util import exec_utils


class Variants(Enum):
    XML_DCR_PORTAL = xml_dcr_portal


DEFAULT_VARIANT = Variants.XML_DCR_PORTAL


def apply(path, variant=DEFAULT_VARIANT, parameters=None):
    if parameters is None:
        parameters = {}

    return exec_utils.get_variant(variant).apply(path, parameters=parameters)


def deserialize(dcr_string, variant=DEFAULT_VARIANT, parameters=None):
    if parameters is None:
        parameters = {}

    return exec_utils.get_variant(variant).import_from_string(dcr_string, parameters=parameters)
