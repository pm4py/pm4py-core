from enum import Enum
from pm4py.util import exec_utils
from typing import Optional, Dict, Any, Union
from pm4py.objects.log.obj import EventLog
from pm4py.objects.conversion.log import converter as log_converter
import pandas as pd
from copy import copy


class Parameters(Enum):
    RETURN_LEGACY_LOG_OBJECT = "return_legacy_log_object"


def apply(log_path: str, parameters: Optional[Dict[Any, Any]] = None) -> Union[EventLog, pd.DataFrame]:
    if parameters is None:
        parameters = {}

    return_legacy_log_object = exec_utils.get_param_value(Parameters.RETURN_LEGACY_LOG_OBJECT, parameters, True)

    import rustxes

    log = rustxes.import_xes(log_path)
    log = log[0].to_pandas()

    if return_legacy_log_object:
        this_parameters = copy(parameters)
        this_parameters["stream_postprocessing"] = True

        log = log_converter.apply(log, variant=log_converter.Variants.TO_EVENT_LOG, parameters=this_parameters)

    return log
