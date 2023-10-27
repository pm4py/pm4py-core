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
from pm4py.util.constants import CASE_CONCEPT_NAME
from pm4py.statistics.traces.generic.pandas.case_statistics import get_variants_df
from pm4py.util.constants import PARAMETER_CONSTANT_CASEID_KEY, PARAMETER_CONSTANT_ACTIVITY_KEY
from enum import Enum
from pm4py.util import exec_utils
from copy import copy
from typing import Optional, Dict, Any, Union, List
import pandas as pd
from pm4py.util import constants


class Parameters(Enum):
    CASE_ID_KEY = PARAMETER_CONSTANT_CASEID_KEY
    ACTIVITY_KEY = PARAMETER_CONSTANT_ACTIVITY_KEY
    DECREASING_FACTOR = "decreasingFactor"
    POSITIVE = "positive"


def apply(df: pd.DataFrame, admitted_prefixes: List[str], parameters: Optional[Dict[Union[str, Parameters], Any]] = None) -> pd.DataFrame:
    """
    Apply a filter on variants

    Parameters
    -----------
    df
        Dataframe
    admitted_prefixes
        List of admitted prefixes (to include/exclude)
    parameters
        Parameters of the algorithm, including:
            Parameters.CASE_ID_KEY -> Column that contains the Case ID
            Parameters.ACTIVITY_KEY -> Column that contains the activity
            Parameters.POSITIVE -> Specifies if the filter should be applied including traces (positive=True)
            or excluding traces (positive=False)
            variants_df -> If provided, avoid recalculation of the variants dataframe

    Returns
    -----------
    df
        Filtered dataframe
    """
    if parameters is None:
        parameters = {}

    case_id_glue = exec_utils.get_param_value(Parameters.CASE_ID_KEY, parameters, CASE_CONCEPT_NAME)
    positive = exec_utils.get_param_value(Parameters.POSITIVE, parameters, True)
    variants_df = parameters["variants_df"] if "variants_df" in parameters else get_variants_df(df,
                                                                                                parameters=parameters)

    admitted_prefixes = list(admitted_prefixes)
    first_case_variant = variants_df["variant"].iloc[0]
    if isinstance(first_case_variant, tuple):
        # manage that as tuple
        variants_df = variants_df.copy()
        variants_df["variant"] = variants_df["variant"].apply(lambda x: constants.DEFAULT_VARIANT_SEP.join(list(x)))
        admitted_prefixes = [constants.DEFAULT_VARIANT_SEP.join(x) for x in admitted_prefixes]
    admitted_prefixes = tuple(admitted_prefixes)

    variants_df = variants_df[variants_df["variant"].str.startswith(admitted_prefixes)]

    i1 = df.set_index(case_id_glue).index
    i2 = variants_df.index
    if positive:
        ret = df[i1.isin(i2)]
    else:
        ret = df[~i1.isin(i2)]

    ret.attrs = copy(df.attrs) if hasattr(df, 'attrs') else {}
    return ret
