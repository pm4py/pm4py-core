from pm4py.statistics.performance_spectrum.versions import dataframe, log
import pandas as pd
from enum import Enum
from pm4py.util import exec_utils
from pm4py.statistics.performance_spectrum.parameters import Parameters
from pm4py.statistics.performance_spectrum.outputs import Outputs


class Variants(Enum):
    DATAFRAME = dataframe
    LOG = log


VERSIONS = {Variants.DATAFRAME, Variants.LOG}


def apply(log, list_activities, parameters=None):
    """
    Finds the performance spectrum provided a log/dataframe
    and a list of activities

    Parameters
    -------------
    log
        Event log/Dataframe
    list_activities
        List of activities interesting for the performance spectrum (at least two)
    parameters
        Parameters of the algorithm, including:
            - Parameters.ACTIVITY_KEY
            - Parameters.TIMESTAMP_KEY

    Returns
    -------------
    ps
        Performance spectrum object (dictionary)
    """
    from pm4py.objects.conversion.log import converter as log_conversion

    if parameters is None:
        parameters = {}

    sample_size = exec_utils.get_param_value(Parameters.PARAMETER_SAMPLE_SIZE, parameters, 10000)

    if len(list_activities) < 2:
        raise Exception("performance spectrum can be applied providing at least two activities!")

    if type(log) is pd.DataFrame:
        points = exec_utils.get_variant(Variants.DATAFRAME).apply(log, list_activities, sample_size, parameters)
    else:
        points = exec_utils.get_variant(Variants.LOG).apply(log_conversion.apply(log), list_activities, sample_size,
                                                            parameters)

    ps = {Outputs.LIST_ACTIVITIES.value: list_activities, Outputs.POINTS.value: points}

    return ps
