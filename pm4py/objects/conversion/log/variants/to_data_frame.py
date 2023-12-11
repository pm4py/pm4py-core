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
from enum import Enum

from pm4py.objects.conversion.log.variants import to_event_stream
from pm4py.objects.log import obj as log_instance
from pm4py.objects.conversion.log import constants
from copy import copy
from pm4py.util import constants as pm4_constants
from pm4py.util import pandas_utils


class Parameters(Enum):
    DEEP_COPY = constants.DEEPCOPY
    STREAM_POST_PROCESSING = constants.STREAM_POSTPROCESSING
    CASE_ATTRIBUTE_PREFIX = "case_attribute_prefix"


def apply(log, parameters=None):
    """
    Converts a provided event log object into a Pandas dataframe. As a basis, an EventStream object is used.
    In case an EventLog object is given, it is first converted to an EventStream object.
    Within the conversion, the order is not changed, i.e., the order imposed by the iterator is used.

    Parameters
    -----------

    log :class:`pm4py.log.log.EventLog`
        Event log object, can either be an EventLog object, EventStream Object or Pandas dataframe

    parameters :class:`dict`
        Parameters of the algorithm (currently, this converter is parameter free)

    Returns
    -----------
    df
        Pandas dataframe
    """
    import pandas as pd

    if parameters is None:
        parameters = dict()
    if pandas_utils.check_is_pandas_dataframe(log):
        return log

    if type(log) is log_instance.EventLog:
        new_parameters = copy(parameters)
        new_parameters["deepcopy"] = False
        log = to_event_stream.apply(log, parameters=new_parameters)

    transf_log = [dict(x) for x in log]
    df = pandas_utils.instantiate_dataframe(transf_log)

    df.attrs = copy(log.properties)
    if pm4_constants.PARAMETER_CONSTANT_CASEID_KEY in df.attrs:
        del df.attrs[pm4_constants.PARAMETER_CONSTANT_CASEID_KEY]

    return df
