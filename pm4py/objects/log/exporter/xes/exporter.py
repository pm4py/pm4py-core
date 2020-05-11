from enum import Enum

from pm4py.objects.conversion.log import converter as log_conversion
from pm4py.objects.log.exporter.xes.variants import etree_xes_exp
from pm4py.util import exec_utils


class Variants(Enum):
    ETREE = etree_xes_exp


def __export_log_as_string(log, variant=Variants.ETREE, parameters=None):
    """
    Method to export a XES from a log as a string

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
    variant = variant if isinstance(variant, Variants) else Variants.ETREE
    return variant.value.apply(log_conversion.apply(log, parameters=parameters), parameters=parameters)


def __export_log(log, output_file_path, variant=Variants.ETREE, parameters=None):
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
    __export_log(log, output_file_path, variant=variant,
                 parameters=parameters)
