from enum import Enum

import deprecation

from pm4py.objects.log.importer.xes.variants import iterparse, line_by_line
from pm4py.objects.log.util import compression
from pm4py.objects.log.util import string_to_file
from pm4py.util import exec_utils


class Variants(Enum):
    ITERPARSE = iterparse
    LINE_BY_LINE = line_by_line


# deprecated variant keys; remove in 2.0.0
ITERPARSE = Variants.ITERPARSE
NONSTANDARD = Variants.LINE_BY_LINE
VERSIONS = {ITERPARSE, NONSTANDARD}


def __import_log_from_string(log_string, parameters=None, variant=Variants.ITERPARSE):
    """
    Imports a log from a string

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

    temp_file = string_to_file.import_string_to_temp_file(log_string, "xes")
    return apply(temp_file, parameters=parameters, variant=variant)


@deprecation.deprecated(deprecated_in='1.3.0', removed_in='2.0.0', current_version='',
                        details='Use apply method instead')
def __import_log(path, parameters=None, variant=Variants.ITERPARSE):
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

    # supporting .xes.gz file types
    if path.endswith("gz"):
        path = compression.decompress(path)

    # backward compatibility
    if variant == 'nonstandard':
        variant = Variants.LINE_BY_LINE
    elif variant == 'iterparse':
        variant = Variants.ITERPARSE

    return exec_utils.get_variant(variant).apply(path, parameters=parameters)


def apply(path, parameters=None, variant=Variants.ITERPARSE):
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
    # supporting .xes.gz file types
    if path.endswith("gz"):
        path = compression.decompress(path)

    # backward compatibility
    if variant == 'nonstandard':
        variant = Variants.LINE_BY_LINE
    elif variant == 'iterparse':
        variant = Variants.ITERPARSE

    return variant.value.apply(path, parameters=parameters)
