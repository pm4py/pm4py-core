from enum import Enum

import pandas as pd

from pm4py.objects.conversion.log.variants import to_event_stream
from pm4py.objects.log import log as log_instance


class Parameters(Enum):
    DEEP_COPY = False
    CASE_ATTRIBUTE_PREFIX = 'case:'


def __parse_params(parameters):
    new_params = dict()
    if Parameters.DEEP_COPY in parameters:
        new_params[to_event_stream.Parameters.DEEP_COPY] = parameters[Parameters.DEEP_COPY]
    if Parameters.CASE_ATTRIBUTE_PREFIX in parameters:
        new_params[to_event_stream.Parameters.CASE_ATTRIBUTE_PREFIX] = parameters[Parameters.CASE_ATTRIBUTE_PREFIX]
    return new_params


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
    if parameters is None:
        parameters = dict()
    if isinstance(log, pd.core.frame.DataFrame):
        return log
    if type(log) is log_instance.EventLog:
        log = to_event_stream.apply(log, parameters=__parse_params(parameters))
    transf_log = [dict(x) for x in log]
    df = pd.DataFrame.from_dict(transf_log)
    return df
