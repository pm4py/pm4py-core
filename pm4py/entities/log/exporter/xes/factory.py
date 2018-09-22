from pm4py.entities.log.exporter.xes.versions import etree_xes_exp
from pm4py.entities.log.util import compression

ETREE = "etree"
VERSIONS_STRING = {ETREE: etree_xes_exp.export_log_as_string}
VERSIONS = {ETREE: etree_xes_exp.export_log}

def export_log_as_string(log, variant="etree", parameters=None):
    """
    Factory method to export a XES from an trace log as a string

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
    return VERSIONS_STRING[variant](log, parameters=parameters)

def export_log(log, outputFilePath, variant="etree", parameters=None):
    """
    Factory method to export a XES from an trace log

    Parameters
    -----------
    log
        Trace log
    outputFilePath
        Output file path
    variant
        Selected variant of the algorithm
    parameters
        Parameters of the algorithm:
            compress -> Indicates that the XES file must be compressed
    """
    if parameters is None:
        parameters = {}
    VERSIONS[variant](log, outputFilePath, parameters=parameters)
    if "compress" in parameters and parameters["compress"]:
        compression.compress(outputFilePath)

def apply(log, outputFilePath, variant="etree", parameters=None):
    """
    Factory method to export a XES from an trace log

    Parameters
    -----------
    log
        Trace log
    outputFilePath
        Output file path
    variant
        Selected variant of the algorithm
    parameters
        Parameters of the algorithm:
            compress -> Indicates that the XES file must be compressed
    """
    export_log(log, outputFilePath, variant=variant, parameters=parameters)