from pm4py.log.exporter.xes.versions import etree_xes_exp

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
        Parameters of the algorithm
    """
    VERSIONS[variant](log, outputFilePath, parameters=parameters)

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
        Parameters of the algorithm
    """
    export_log(log, outputFilePath, variant=variant, parameters=parameters)