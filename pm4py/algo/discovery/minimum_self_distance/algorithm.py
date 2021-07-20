from enum import Enum
from typing import Union, Optional, Dict, Any

import pandas as pd

from pm4py.algo.discovery.minimum_self_distance.variants import log, pandas
from pm4py.objects.log.obj import EventLog, EventStream
from pm4py.util import exec_utils


class Variants(Enum):
    LOG = log
    PANDAS = pandas


def apply(log_obj: Union[EventLog, pd.DataFrame, EventStream], variant: Union[str, None] = None,
          parameters: Optional[Dict[Any, Any]] = None):
    if parameters is None:
        parameters = {}

    if variant is None:
        if isinstance(log_obj, pd.DataFrame):
            variant = Variants.PANDAS
        else:
            variant = Variants.LOG

    return exec_utils.get_variant(variant).apply(log_obj, parameters=parameters)
