from pm4py.log.exporter.xes.versions import etree_xes_exp

def export_log(log, outputFilePath):
    """
    Export XES log from a PM4PY trace log

    Parameters
    ----------
    log: :class:`pm4py.log.log.TraceLog`
        PM4PY trace log
    outputFilePath:
        Output file path

    """

    return etree_xes_exp.export_log(log, outputFilePath)