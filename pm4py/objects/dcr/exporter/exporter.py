from enum import Enum
from pm4py.objects.dcr.exporter.variants import xml_simple, xml_dcr_portal


class Variants(Enum):
    XML_SIMPLE = xml_simple
    XML_DCR_PORTAL = xml_dcr_portal


XML_SIMPLE = Variants.XML_SIMPLE
XML_DCR_PORTAL = Variants.XML_DCR_PORTAL

VERSIONS = {XML_SIMPLE, XML_DCR_PORTAL}


def apply(dcr_graph, path, variant=XML_SIMPLE, **parameters):
    """
    Parameters
    -----------
    input_log
    variant
        Variant of the algorithm to use:
            - DCR_BASIC
            - DCR_SUBPROCESS_TIMED
    parameters
        Algorithm related params
        finaAdditionalConditions: [True or False]
    Returns
    -----------

    """

    if variant is Variants.XML_DCR_PORTAL:
        xml_dcr_portal.export_dcr_xml(dcr_graph, output_file_name=path, **parameters)
    elif variant is Variants.XML_SIMPLE:
        xml_simple.export_dcr_xml(dcr_graph, output_file_name=path, **parameters)