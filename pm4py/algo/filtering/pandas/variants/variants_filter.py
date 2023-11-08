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
from pm4py.statistics.variants.pandas import get as variants_get
from pm4py.util.constants import PARAMETER_CONSTANT_CASEID_KEY, PARAMETER_CONSTANT_ACTIVITY_KEY
from enum import Enum
from pm4py.util import exec_utils
from copy import copy
from typing import Optional, Dict, Any, Union, List
import pandas as pd


class Parameters(Enum):
    CASE_ID_KEY = PARAMETER_CONSTANT_CASEID_KEY
    ACTIVITY_KEY = PARAMETER_CONSTANT_ACTIVITY_KEY
    DECREASING_FACTOR = "decreasingFactor"
    POSITIVE = "positive"


def apply(df: pd.DataFrame, admitted_variants: List[List[str]], parameters: Optional[Dict[Union[str, Parameters], Any]] = None) -> pd.DataFrame:
    """
    Apply a filter on variants

    Parameters
    -----------
    df
        Dataframe
    admitted_variants
        List of admitted variants (to include/exclude)
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
    variants_df = variants_df[variants_df["variant"].isin(admitted_variants)]
    i1 = df.set_index(case_id_glue).index
    i2 = variants_df.index
    if positive:
        ret = df[i1.isin(i2)]
    else:
        ret = df[~i1.isin(i2)]

    ret.attrs = copy(df.attrs) if hasattr(df, 'attrs') else {}
    return ret


def filter_variants_top_k(log, k, parameters=None):
    """
    Keeps the top-k variants of the log

    Parameters
    -------------
    log
        Event log
    k
        Number of variants that should be kept
    parameters
        Parameters

    Returns
    -------------
    filtered_log
        Filtered log
    """
    if parameters is None:
        parameters = {}

    variants = variants_get.get_variants_count(log, parameters=parameters)
    variant_count = []
    for variant in variants:
        variant_count.append([variant, variants[variant]])
    variant_count = sorted(variant_count, key=lambda x: (x[1], x[0]), reverse=True)
    variant_count = variant_count[:min(k, len(variant_count))]
    variants_to_filter = [x[0] for x in variant_count]

    return apply(log, variants_to_filter, parameters=parameters)


def filter_variants_by_coverage_percentage(log, min_coverage_percentage, parameters=None):
    """
    Filters the variants of the log by a coverage percentage
    (e.g., if min_coverage_percentage=0.4, and we have a log with 1000 cases,
    of which 500 of the variant 1, 400 of the variant 2, and 100 of the variant 3,
    the filter keeps only the traces of variant 1 and variant 2).

    Parameters
    ---------------
    log
        Event log
    min_coverage_percentage
        Minimum allowed percentage of coverage
    parameters
        Parameters

    Returns
    ---------------
    filtered_log
        Filtered log
    """
    if parameters is None:
        parameters = {}

    case_id_glue = exec_utils.get_param_value(Parameters.CASE_ID_KEY, parameters, CASE_CONCEPT_NAME)

    variants = variants_get.get_variants_count(log, parameters=parameters)
    allowed_variants = [x for x, y in variants.items() if y >= min_coverage_percentage * log[case_id_glue].nunique()]

    return apply(log, allowed_variants, parameters=parameters)


def filter_variants_by_maximum_coverage_percentage(log, max_coverage_percentage, parameters=None):
    """
    Filters the variants of the log by a maximum coverage percentage
    (e.g., if max_coverage_percentage=0.4, and we have a log with 1000 cases,
    of which 500 of the variant 1, 400 of the variant 2, and 100 of the variant 3,
    the filter keeps only the traces of variant w and variant 3).

    Parameters
    ---------------
    log
        Event log
    max_coverage_percentage
        Maximum allowed percentage of coverage
    parameters
        Parameters

    Returns
    ---------------
    filtered_log
        Filtered log
    """
    if parameters is None:
        parameters = {}

    case_id_glue = exec_utils.get_param_value(Parameters.CASE_ID_KEY, parameters, CASE_CONCEPT_NAME)

    variants = variants_get.get_variants_count(log, parameters=parameters)
    allowed_variants = [x for x, y in variants.items() if y <= max_coverage_percentage * log[case_id_glue].nunique()]

    return apply(log, allowed_variants, parameters=parameters)