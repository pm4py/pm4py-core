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
from pm4py.objects.ocel.obj import OCEL
from typing import Optional, Dict, Any
from pm4py.objects.ocel.util import ocel_consistency
from enum import Enum
from pm4py.util import exec_utils, constants as pm4_constants


class Parameters(Enum):
    ENCODING = "encoding"


def apply(ocel: OCEL, output_path: str, objects_path=None, parameters: Optional[Dict[Any, Any]] = None):
    """
    Exports an object-centric event log in a CSV file, using Pandas as backend

    Parameters
    -----------------
    ocel
        Object-centric event log
    output_path
        Destination file
    objects_path
        Optional path, where the objects dataframe is stored
    parameters
        Parameters of the algorithm
    """
    if parameters is None:
        parameters = {}

    encoding = exec_utils.get_param_value(Parameters.ENCODING, parameters, pm4_constants.DEFAULT_ENCODING)

    ocel = ocel_consistency.apply(ocel, parameters=parameters)

    ocel.get_extended_table().to_csv(output_path, index=False, na_rep="", encoding=encoding)

    if objects_path is not None:
        ocel.objects.to_csv(objects_path, index=False, na_rep="", encoding=encoding)
