import pandas as pd
from pm4py.objects.conversion.log.variants import to_event_log
from pm4py.objects.log import pandas_log_wrapper
from pm4py.objects.log.obj import Trace


def apply(log, parameters=None):
    if parameters is None:
        parameters = {}

    from pm4py.utils import __event_log_deprecation_warning
    __event_log_deprecation_warning(log)
    
    if type(log) is pd.DataFrame:
        return pandas_log_wrapper.PandasLogWrapper(log, parameters=parameters)
    elif type(log) in [pandas_log_wrapper.PandasLogWrapper, Trace]:
        return log

    return to_event_log.apply(log, parameters=parameters)
