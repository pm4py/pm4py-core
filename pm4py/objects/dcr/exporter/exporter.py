from enum import Enum
from pm4py.objects.dcr.exporter.variants import xml_simple,xml_full
from pm4py.util import exec_utils
from typing import Optional, Dict, Any, Union, Tuple


class Variants(Enum):
    DCR_XML_SIMPLE = xml_simple
    DCR_XML_FULL = xml_full


DCR_XML_SIMPLE = Variants.DCR_XML_SIMPLE
DCR_XML_FULL = Variants.DCR_XML_FULL

VERSIONS = {DCR_XML_SIMPLE, DCR_XML_FULL}


def apply(dcr_graph, path, variant=DCR_XML_SIMPLE, **parameters):
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

    if variant is Variants.DCR_XML_FULL:
        xml_full.export_dcr_xml(dcr_graph, output_file_name=path, **parameters)
    elif variant is Variants.DCR_XML_SIMPLE:
        xml_simple.export_dcr_xml(dcr_graph, output_file_name=path, **parameters)