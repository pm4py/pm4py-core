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
from typing import Optional, Dict, Any

import pandas as pd

from pm4py.objects.ocel.obj import OCEL
from pm4py.objects.ocel.util import extended_table
from pm4py.objects.ocel.util import ocel_consistency
from enum import Enum
from pm4py.util import exec_utils, constants as pm4_constants, pandas_utils


class Parameters(Enum):
    ENCODING = "encoding"


def apply(file_path: str, objects_path: str = None, parameters: Optional[Dict[Any, Any]] = None) -> OCEL:
    """
    Imports an object-centric event log from a CSV file, using Pandas as backend

    Parameters
    -----------------
    file_path
        Path to the object-centric event log
    objects_path
        Optional path to a CSV file containing the objects dataframe
    parameters
        Parameters of the algorithm

    Returns
    ------------------
    ocel
        Object-centric event log
    """
    if parameters is None:
        parameters = {}

    encoding = exec_utils.get_param_value(Parameters.ENCODING, parameters, pm4_constants.DEFAULT_ENCODING)
    table = pandas_utils.read_csv(file_path, index_col=False, encoding=encoding)

    objects = None
    if objects_path is not None:
        objects = pandas_utils.read_csv(objects_path, index_col=False, encoding=encoding)

    ocel = extended_table.get_ocel_from_extended_table(table, objects, parameters=parameters)
    ocel = ocel_consistency.apply(ocel, parameters=parameters)

    return ocel
