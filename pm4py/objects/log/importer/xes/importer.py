import importlib.util
from enum import Enum

from pm4py.objects.log.importer.xes.variants import iterparse, line_by_line, iterparse_mem_compressed, iterparse_20, chunk_regex, rustxes


class Variants(Enum):
    ITERPARSE = iterparse
    LINE_BY_LINE = line_by_line
    ITERPARSE_MEM_COMPRESSED = iterparse_mem_compressed
    ITERPARSE_20 = iterparse_20
    CHUNK_REGEX = chunk_regex
    RUSTXES = rustxes


if importlib.util.find_spec("lxml"):
    DEFAULT_VARIANT = Variants.ITERPARSE
else:
    DEFAULT_VARIANT = Variants.CHUNK_REGEX


def apply(path, parameters=None, variant=DEFAULT_VARIANT):
    """
    Import a XES log into a EventLog object

    Parameters
    -----------
    path
        Log path
    parameters
        Parameters of the algorithm, including
            Parameters.TIMESTAMP_SORT -> Specify if we should sort log by timestamp
            Parameters.TIMESTAMP_KEY -> If sort is enabled, then sort the log by using this key
            Parameters.REVERSE_SORT -> Specify in which direction the log should be sorted
            Parameters.INSERT_TRACE_INDICES -> Specify if trace indexes should be added as event attribute for each event
            Parameters.MAX_TRACES -> Specify the maximum number of traces to import from the log (read in order in the XML file)
    variant
        Variant of the algorithm to use, including:
            - Variants.ITERPARSE
            - Variants.LINE_BY_LINE

    Returns
    -----------
    log
        Trace log object
    """
    if variant == 'nonstandard':
        variant = Variants.LINE_BY_LINE
    elif variant == 'iterparse':
        variant = Variants.ITERPARSE
    elif variant == 'chunk_regex':
        variant = Variants.CHUNK_REGEX
    elif variant == "line_by_line":
        variant = Variants.LINE_BY_LINE
    elif variant == "iterparse_20":
        variant = Variants.ITERPARSE_20
    elif variant == "iterparse_mem_compressed":
        variant = Variants.ITERPARSE_MEM_COMPRESSED
    elif variant == "rustxes":
        variant = Variants.RUSTXES

    log = variant.value.apply(path, parameters=parameters)

    return log

    #from pm4py.objects.conversion.log import converter as log_converter
    #return log_converter.apply(log, variant=log_converter.Variants.TO_DATA_FRAME, parameters=parameters)


def deserialize(log_string, parameters=None, variant=DEFAULT_VARIANT):
    """
    Deserialize a text/binary string representing a XES log

    Parameters
    -----------
    log_string
        String that contains the XES
    parameters
        Parameters of the algorithm, including
            Parameters.TIMESTAMP_SORT -> Specify if we should sort log by timestamp
            Parameters.TIMESTAMP_KEY -> If sort is enabled, then sort the log by using this key
            Parameters.REVERSE_SORT -> Specify in which direction the log should be sorted
            Parameters.INSERT_TRACE_INDICES -> Specify if trace indexes should be added as event attribute for each event
            Parameters.MAX_TRACES -> Specify the maximum number of traces to import from the log (read in order in the XML file)
    variant
        Variant of the algorithm to use, including:
            - Variants.ITERPARSE
            - Variants.LINE_BY_LINE

    Returns
    -----------
    log
        Trace log object
    """
    if parameters is None:
        parameters = {}

    return variant.value.import_from_string(log_string, parameters=parameters)
