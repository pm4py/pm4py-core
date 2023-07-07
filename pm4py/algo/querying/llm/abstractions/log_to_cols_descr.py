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

from pm4py.objects.log.obj import EventLog, EventStream
import pandas as pd
from typing import Optional, Dict, Any, Union
from pm4py.objects.conversion.log import converter as log_converter
from enum import Enum
from pm4py.util import exec_utils, constants


class Parameters(Enum):
    MAX_LEN = "max_len"
    CASE_ID_KEY = constants.PARAMETER_CONSTANT_CASEID_KEY


def apply(log_obj: Union[EventLog, EventStream, pd.DataFrame], parameters: Optional[Dict[Any, Any]] = None) -> str:
    if parameters is None:
        parameters = {}

    log_obj = log_converter.apply(log_obj, variant=log_converter.Variants.TO_DATA_FRAME, parameters=parameters)
    max_len = exec_utils.get_param_value(Parameters.MAX_LEN, parameters, constants.OPENAI_MAX_LEN)
    case_id_key = exec_utils.get_param_value(Parameters.CASE_ID_KEY, parameters, constants.CASE_CONCEPT_NAME)

    log_obj = log_obj[[x for x in log_obj.columns if x != case_id_key]]
    cols_dtypes = {x: str(log_obj[x].dtype) for x in log_obj.columns}

    num_nans = {}
    lst_values = []

    for x, y in cols_dtypes.items():
        num_nans[x] = log_obj[x].isna().sum()
        if "object" in y or "string" in y or "bool" in y:
            values = log_obj[x].value_counts().to_dict()
            if len(values) > 1:
                for v, co in values.items():
                    lst_values.append((x, v, co))

    lst_values = sorted(lst_values, key=lambda x: (x[2], x[0], x[1]), reverse=True)
    ret = {}
    curr_len = 0

    for x, y in cols_dtypes.items():
        if "float" in y or "double" in y or "date" in y:
            quantiles = " quantiles: " + str(log_obj[x].quantile([0.0, 0.25, 0.5, 0.75, 1.0]).to_dict())
            nans = " empty: "+str(num_nans[x])+" "
            curr_len += len(x) + len(nans) + len(quantiles) + 1

            ret[x] = nans + quantiles

    for el in lst_values:
        if curr_len >= max_len:
            break

        if not el[0] in ret:
            stru = " empty: "+str(num_nans[el[0]]) + " values:"
            ret[el[0]] = stru
            curr_len += len(el[0]) + len(stru) + 9

        stru = " ("+str(el[1])+"; freq. "+str(el[2])+")"
        ret[el[0]] += stru
        curr_len += len(stru)

    keys = sorted(list(ret))
    ret = [k + " "+ret[k] for k in keys]
    return "\n".join(ret)


