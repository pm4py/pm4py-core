import pandas
import deprecation

from pm4py import util as pmutil
from pm4py.objects.conversion.log import converter as log_conversion
from pm4py.util import xes_constants as xes_util
from pm4py.visualization.common import gview
from pm4py.visualization.common import save as gsave
from pm4py.objects.log.util import dataframe_utils
from pm4py.visualization.petrinet.versions import wo_decoration, token_decoration, greedy_decoration, alignments

WO_DECORATION = "wo_decoration"
FREQUENCY_DECORATION = "frequency"
PERFORMANCE_DECORATION = "performance"
FREQUENCY_GREEDY = "frequency_greedy"
PERFORMANCE_GREEDY = "performance_greedy"
ALIGNMENTS = "alignments"

RANKDIR = "set_rankdir"

VERSIONS = {WO_DECORATION: wo_decoration.apply, FREQUENCY_DECORATION: token_decoration.apply_frequency,
            PERFORMANCE_DECORATION: token_decoration.apply_performance,
            FREQUENCY_GREEDY: greedy_decoration.apply_frequency,
            PERFORMANCE_GREEDY: greedy_decoration.apply_performance,
            ALIGNMENTS: alignments.apply}


@deprecation.deprecated(deprecated_in='1.3.0', removed_in='2.0.0', current_version='',
                        details='Use visualizer module instead.')
def apply(net, initial_marking=None, final_marking=None, log=None, aggregated_statistics=None, parameters=None,
          variant="wo_decoration"):
    if parameters is None:
        parameters = {}
    timestamp_key = parameters[
        pmutil.constants.PARAMETER_CONSTANT_TIMESTAMP_KEY] if pmutil.constants.PARAMETER_CONSTANT_TIMESTAMP_KEY in parameters else pmutil.xes_constants.DEFAULT_TIMESTAMP_KEY
    if log is not None:
        if isinstance(log, pandas.core.frame.DataFrame):
            log = dataframe_utils.convert_timestamp_columns_in_df(log, timest_columns=[
                timestamp_key])
        log = log_conversion.apply(log, parameters, log_conversion.TO_EVENT_LOG)
    return VERSIONS[variant](net, initial_marking, final_marking, log=log, aggregated_statistics=aggregated_statistics,
                             parameters=parameters)


@deprecation.deprecated(deprecated_in='1.3.0', removed_in='2.0.0', current_version='',
                        details='Use visualizer module instead.')
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


@deprecation.deprecated(deprecated_in='1.3.0', removed_in='2.0.0', current_version='',
                        details='Use visualizer module instead.')
def view(gviz):
    """
    View the diagram

    Parameters
    -----------
    gviz
        GraphViz diagram
    """
    return gview.view(gviz)
