from enum import Enum
from pm4py.util import exec_utils
from pm4py.streaming.importer.csv.variants import csv_event_stream


class Variants(Enum):
    CSV_EVENT_STREAM = csv_event_stream


DEFAULT_VARIANT = Variants.CSV_EVENT_STREAM


def apply(path, variant=DEFAULT_VARIANT, parameters=None):
    """
    Reads a stream object from a CSV file

    Parameters
    ---------------
    path
        Path to the CSV file
    variant
        Variant of the importer, possible values:
         - Variants.CSV_EVENT_STREAM
    parameters
        Parameters of the importer

    Returns
    --------------
    stream_obj
        Stream object
    """
    return exec_utils.get_variant(variant).apply(path, parameters=parameters)
