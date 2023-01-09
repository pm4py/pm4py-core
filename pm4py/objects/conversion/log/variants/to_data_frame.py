from enum import Enum

from pm4py.objects.conversion.log.variants import to_event_stream
from pm4py.objects.log import obj as log_instance
from pm4py.objects.conversion.log import constants
from copy import copy
from pm4py.util import constants as pm4_constants
import numpy as np
from datetime import datetime

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
    if isinstance(log, pd.core.frame.DataFrame):
        return log
    if type(log) is log_instance.EventLog:
        new_parameters = copy(parameters)
        new_parameters["deepcopy"] = False
        log = to_event_stream.apply(log, parameters=new_parameters)

    transf_log = [dict(x) for x in log]

    # Pandas 1.5.x has problems in managing datetime.datetime types
    # ensure the dates are provided as np.datetime64 which is supported correctly
    # until a proper fix on the Pandas side is provided
    for ev in transf_log:
        for attr in ev:
            if isinstance(ev[attr], datetime):
                ev[attr] = np.datetime64(ev[attr])

    df = pd.DataFrame.from_dict(transf_log)
    df.attrs = copy(log.properties)
    if pm4_constants.PARAMETER_CONSTANT_CASEID_KEY in df.attrs:
        del df.attrs[pm4_constants.PARAMETER_CONSTANT_CASEID_KEY]

    return df
