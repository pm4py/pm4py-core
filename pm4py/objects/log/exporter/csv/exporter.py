from enum import Enum

from pm4py.objects.log.exporter.csv.variants import pandas_csv_exp
from pm4py.util import exec_utils


class Variants(Enum):
    PANDAS = pandas_csv_exp


def apply(log, output_file_path, variant=Variants.PANDAS, parameters=None):
    """
    Factory method to export a CSV from an event log

    Parameters
    -----------
    log
        Event log
    output_file_path
        Output file path
    variant
        Selected variant of the algorithm.
            - Variants.PANDAS
    parameters
        Parameters of the algorithm
    """
    exec_utils.get_variant(variant).apply(log, output_file_path, parameters=parameters)
