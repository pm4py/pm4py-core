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
import pandas as pd
from enum import Enum
from pm4py.util import constants, xes_constants, pandas_utils, exec_utils
import numpy as np
from collections import Counter
from typing import Tuple, Dict, Collection
import importlib.util


class Parameters(Enum):
    CASE_ID_KEY = constants.PARAMETER_CONSTANT_CASEID_KEY
    ACTIVITY_KEY = constants.PARAMETER_CONSTANT_ACTIVITY_KEY
    TIMESTAMP_KEY = constants.PARAMETER_CONSTANT_TIMESTAMP_KEY
    INDEX_KEY = "index_key"


def apply(dataframe: pd.DataFrame, parameters=None) -> Tuple[Dict[Collection[str], int], Dict[str, Collection[str]]]:
    """
    Efficient method returning the variants from a Pandas dataframe (through Numpy)

    Minimum viable example:

        import pandas as pd
        import pm4py
        from pm4py.objects.log.util import pandas_numpy_variants

        dataframe = pd.read_csv('tests/input_data/receipt.csv')
        dataframe = pm4py.format_dataframe(dataframe)
        variants_dict, case_variant = pandas_numpy_variants.apply(dataframe)


    Parameters
    ------------------
    dataframe
        Dataframe
    parameters
        Parameters of the algorithm, including:
        - Parameters.CASE_ID_KEY => the case identifier
        - Parameters.ACTIVITY_KEY => the activity
        - Parameters.TIMESTAMP_KEY => the timestamp
        - Parameters.INDEX_KEY => the index

    Returns
    ------------------
    variants_dict
        Dictionary associating to each variant the number of occurrences in the dataframe
    case_variant
        Dictionary associating to each case identifier the corresponding variant
    """
    if parameters is None:
        parameters = {}

    case_id_key = exec_utils.get_param_value(Parameters.CASE_ID_KEY, parameters, constants.CASE_CONCEPT_NAME)
    activity_key = exec_utils.get_param_value(Parameters.ACTIVITY_KEY, parameters, xes_constants.DEFAULT_NAME_KEY)
    timestamp_key = exec_utils.get_param_value(Parameters.TIMESTAMP_KEY, parameters, xes_constants.DEFAULT_TIMESTAMP_KEY)
    index_key = exec_utils.get_param_value(Parameters.INDEX_KEY, parameters, constants.DEFAULT_INDEX_KEY)

    if not (hasattr(dataframe, "attrs") and dataframe.attrs):
        # dataframe has not been initialized through format_dataframe
        dataframe = pandas_utils.insert_index(dataframe, index_key)
        dataframe.sort_values([case_id_key, timestamp_key, index_key])

    case_variant = dict()

    if importlib.util.find_spec("cudf"):
        case_variant = dataframe.groupby(case_id_key)[activity_key].agg(list).to_dict()
        case_variant = {x: tuple(y) for x, y in case_variant.items()}
        variants_counter = Counter(case_variant.values())
    else:
        variants_counter = Counter()
        cases = dataframe[case_id_key].to_numpy()
        activities = dataframe[activity_key].to_numpy()

        c_unq, c_ind, c_counts = np.unique(cases, return_index=True, return_counts=True)

        for i in range(len(c_ind)):
            si = c_ind[i]
            ei = si + c_counts[i]
            acts = tuple(activities[si:ei])
            variants_counter[acts] += 1
            case_variant[c_unq[i]] = acts

    # return as Python dictionary
    variants_dict = {x: y for x, y in variants_counter.items()}

    return variants_dict, case_variant
