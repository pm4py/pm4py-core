from enum import Enum

from pm4py.objects.dcr.importer.variants import xml_dcr_portal, xml_simple
from pm4py.util import exec_utils


class Variants(Enum):
    XML_DCR_PORTAL = xml_dcr_portal
    XML_SIMPLE = xml_simple


XML_SIMPLE = Variants.XML_SIMPLE
XML_DCR_PORTAL = Variants.XML_DCR_PORTAL
DCR_JS_PORTAL = Variants.XML_DCR_PORTAL


def apply(path, variant=XML_DCR_PORTAL, parameters=None):
    '''
    Reads a DCR Graph from an XML file

    Parameters
    ----------
    path
        Path to the XML file
    variant
        Variants of the importer to use:
            - Variants.XML_DCR_PORTAL
            - Variants.XML_SIMPLE
    parameters
        Parameters of the importer
    '''
    if parameters is None:
        parameters = {}

    return exec_utils.get_variant(variant).apply(path, parameters=parameters)


def deserialize(dcr_string, variant=XML_DCR_PORTAL, parameters=None):
    if parameters is None:
        parameters = {}

    return exec_utils.get_variant(variant).import_from_string(dcr_string, parameters=parameters)
