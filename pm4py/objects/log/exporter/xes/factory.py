import deprecation

from pm4py.objects.conversion.log import converter as log_converter
from pm4py.objects.log.exporter.xes.versions import etree_xes_exp
from pm4py.objects.log.util import compression

ETREE = "etree"
VERSIONS_STRING = {ETREE: etree_xes_exp.__export_log_as_string}
VERSIONS = {ETREE: etree_xes_exp.__export_log}


@deprecation.deprecated(deprecated_in='1.3.0', removed_in='2.0.0', current_version='',
                        details='Use exporter entrypoint instead')
def export_log_as_string(log, variant="etree", parameters=None):
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
    return VERSIONS_STRING[variant](log_converter.apply(log, parameters=parameters), parameters=parameters)


@deprecation.deprecated(deprecated_in='1.3.0', removed_in='2.0.0', current_version='',
                        details='Use exporter entrypoint instead')
def export_log(log, output_file_path, variant="etree", parameters=None):
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
            compress -> Indicates that the XES file must be compressed
    """
    if parameters is None:
        parameters = {}
    VERSIONS[variant](log_converter.apply(log, parameters=parameters), output_file_path, parameters=parameters)
    if "compress" in parameters and parameters["compress"]:
        compression.compress(output_file_path)


@deprecation.deprecated(deprecated_in='1.3.0', removed_in='2.0.0', current_version='',
                        details='Use exporter entrypoint instead')
def apply(log, output_file_path, variant="etree", parameters=None):
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
            compress -> Indicates that the XES file must be compressed
    """
    export_log(log_converter.apply(log, parameters=parameters), output_file_path, variant=variant,
               parameters=parameters)
