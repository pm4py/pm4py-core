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
from typing import Union, Optional, Dict, Any

import pandas as pd

from pm4py.algo.discovery.minimum_self_distance.variants import log, pandas
from pm4py.objects.log.obj import EventLog, EventStream
from pm4py.util import exec_utils, pandas_utils


class Variants(Enum):
    LOG = log
    PANDAS = pandas


def apply(log_obj: Union[EventLog, pd.DataFrame, EventStream], variant: Union[str, None] = None,
          parameters: Optional[Dict[Any, Any]] = None) -> Dict[str, int]:
    if parameters is None:
        parameters = {}

    if variant is None:
        if pandas_utils.check_is_pandas_dataframe(log_obj):
            variant = Variants.PANDAS
        else:
            variant = Variants.LOG

    return exec_utils.get_variant(variant).apply(log_obj, parameters=parameters)
