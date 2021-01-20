'''
    This file is part of PM4Py (More Info: https://pm4py.fit.fraunhofer.de).

    PM4Py is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    PM4Py is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with PM4Py.  If not, see <https://www.gnu.org/licenses/>.
'''
from pm4py.statistics.performance_spectrum.variants import dataframe, log
from enum import Enum
from pm4py.util import exec_utils
from pm4py.statistics.performance_spectrum.parameters import Parameters
from pm4py.statistics.performance_spectrum.outputs import Outputs
import pkgutil


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

    points = None

    if pkgutil.find_loader("pandas"):
        import pandas as pd
        if type(log) is pd.DataFrame:
            points = exec_utils.get_variant(Variants.DATAFRAME).apply(log, list_activities, sample_size, parameters)

    points = exec_utils.get_variant(Variants.LOG).apply(log_conversion.apply(log), list_activities, sample_size,
                                                        parameters)

    ps = {Outputs.LIST_ACTIVITIES.value: list_activities, Outputs.POINTS.value: points}

    return ps
