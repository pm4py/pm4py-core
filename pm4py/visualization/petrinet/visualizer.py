import pandas

from pm4py import util as pmutil
from pm4py.objects.conversion.log import converter as log_conversion
from pm4py.objects.log.util import dataframe_utils
from pm4py.visualization.common import gview
from pm4py.visualization.common import save as gsave
from pm4py.visualization.petrinet.variants import wo_decoration, alignments, greedy_decoration_performance, \
    greedy_decoration_frequency, token_decoration_performance, token_decoration_frequency
from pm4py.util import exec_utils, xes_constants
from enum import Enum


class Variants(Enum):
    WO_DECORATION = wo_decoration
    FREQUENCY = token_decoration_frequency
    PERFORMANCE = token_decoration_performance
    FREQUENCY_GREEDY = greedy_decoration_frequency
    PERFORMANCE_GREEDY = greedy_decoration_performance
    ALIGNMENTS = alignments


WO_DECORATION = Variants.WO_DECORATION
FREQUENCY_DECORATION = Variants.FREQUENCY
PERFORMANCE_DECORATION = Variants.PERFORMANCE
FREQUENCY_GREEDY = Variants.FREQUENCY_GREEDY
PERFORMANCE_GREEDY = Variants.PERFORMANCE_GREEDY
ALIGNMENTS = Variants.ALIGNMENTS


def apply(net, initial_marking=None, final_marking=None, log=None, aggregated_statistics=None, parameters=None,
          variant=Variants.WO_DECORATION):
    if parameters is None:
        parameters = {}
    if log is not None:
        if isinstance(log, pandas.core.frame.DataFrame):
            log = dataframe_utils.convert_timestamp_columns_in_df(log)
        log = log_conversion.apply(log, parameters, log_conversion.TO_EVENT_LOG)
    return exec_utils.get_variant(variant).apply(net, initial_marking, final_marking, log=log,
                                                 aggregated_statistics=aggregated_statistics,
                                                 parameters=parameters)


def save(gviz, output_file_path):
    """
    Save the diagram

    Parameters
    -----------
    gviz
        GraphViz diagram
    output_file_path
        Path where the GraphViz output should be saved
    """
    gsave.save(gviz, output_file_path)


def view(gviz):
    """
    View the diagram

    Parameters
    -----------
    gviz
        GraphViz diagram
    """
    return gview.view(gviz)


def matplotlib_view(gviz):
    """
    Views the diagram using Matplotlib

    Parameters
    ---------------
    gviz
        Graphviz
    """

    return gview.matplotlib_view(gviz)
