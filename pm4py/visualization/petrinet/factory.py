import pandas

from pm4py import util as pmutil
from pm4py.objects.conversion.log import factory as log_conversion
from pm4py.objects.log.adapters.pandas import csv_import_adapter
from pm4py.objects.log.util import general as log_util
from pm4py.objects.log.util import xes as xes_util
from pm4py.visualization.common import gview
from pm4py.visualization.common import save as gsave
from pm4py.visualization.petrinet.versions import wo_decoration, token_decoration, greedy_decoration

WO_DECORATION = "wo_decoration"
FREQUENCY_DECORATION = "frequency"
PERFORMANCE_DECORATION = "performance"
FREQUENCY_GREEDY = "frequency_greedy"
PERFORMANCE_GREEDY = "performance_greedy"

RANKDIR_LR = "set_rankdir_lr"

VERSIONS = {WO_DECORATION: wo_decoration.apply, FREQUENCY_DECORATION: token_decoration.apply_frequency,
            PERFORMANCE_DECORATION: token_decoration.apply_performance,
            FREQUENCY_GREEDY: greedy_decoration.apply_frequency,
            PERFORMANCE_GREEDY: greedy_decoration.apply_performance}


def apply(net, initial_marking=None, final_marking=None, log=None, aggregated_statistics=None, parameters=None,
          variant="wo_decoration"):
    if parameters is None:
        parameters = {}
    if pmutil.constants.PARAMETER_CONSTANT_ACTIVITY_KEY not in parameters:
        parameters[pmutil.constants.PARAMETER_CONSTANT_ACTIVITY_KEY] = xes_util.DEFAULT_NAME_KEY
    if pmutil.constants.PARAMETER_CONSTANT_TIMESTAMP_KEY not in parameters:
        parameters[pmutil.constants.PARAMETER_CONSTANT_TIMESTAMP_KEY] = xes_util.DEFAULT_TIMESTAMP_KEY
    if pmutil.constants.PARAMETER_CONSTANT_CASEID_KEY not in parameters:
        parameters[pmutil.constants.PARAMETER_CONSTANT_CASEID_KEY] = log_util.CASE_ATTRIBUTE_GLUE
    if log is not None:
        if isinstance(log, pandas.core.frame.DataFrame):
            log = csv_import_adapter.convert_timestamp_columns_in_df(log, timest_columns=[
                parameters[pmutil.constants.PARAMETER_CONSTANT_TIMESTAMP_KEY]])
        log = log_conversion.apply(log, parameters, log_conversion.TO_EVENT_LOG)
    return VERSIONS[variant](net, initial_marking, final_marking, log=log, aggregated_statistics=aggregated_statistics,
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
