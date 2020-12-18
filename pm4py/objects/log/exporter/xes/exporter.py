from enum import Enum

from pm4py.objects.conversion.log import converter as log_conversion
from pm4py.objects.log.exporter.xes.variants import etree_xes_exp, line_by_line
from pm4py.util import exec_utils


class Variants(Enum):
    ETREE = etree_xes_exp
    LINE_BY_LINE = line_by_line


def apply(log, output_file_path, variant=Variants.ETREE, parameters=None):
    """
    Method to export a XES from a log

    Parameters
    -----------
    log
        Trace log
    output_file_path
        Output file path
    variant
        Selected variant of the algorithm
    parameters
        Parameters of the algorithm:
            Parameters.COMPRESS -> Indicates that the XES file must be compressed
    """
    parameters = dict() if parameters is None else parameters
    return exec_utils.get_variant(variant).apply(log_conversion.apply(log, parameters=parameters), output_file_path,
                                                 parameters=parameters)


def serialize(log, variant=Variants.ETREE, parameters=None):
    """
    Serialize a log into a binary string containing the XES of the log

    Parameters
    -----------
    log
        Trace log
    variant
        Selected variant of the algorithm
    parameters
        Parameters of the algorithm

    Returns
    -----------
    string
        String describing the XES
    """
    parameters = dict() if parameters is None else parameters

    log_string = exec_utils.get_variant(variant).export_log_as_string(log_conversion.apply(log, parameters=parameters),
                                                                      parameters=parameters)

    return log_string
