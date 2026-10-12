from enum import Enum
from typing import Optional, Dict, Any, Union
import polars as pl
from pm4py.util import constants, xes_constants, exec_utils


class Parameters(Enum):
    ACTIVITY_KEY = constants.PARAMETER_CONSTANT_ACTIVITY_KEY
    CASE_ID_KEY = constants.PARAMETER_CONSTANT_CASEID_KEY


def apply(
    lf: pl.LazyFrame,
    parameters: Optional[Dict[Union[str, Parameters], Any]] = None,
) -> Dict[str, int]:
    """
    Associates to each activity (with at least one rework) the number of cases in the log for which
    the rework happened.

    Parameters
    ------------------
    lf
        LazyFrame
    parameters
        Parameters of the algorithm, including:
        - Parameters.ACTIVITY_KEY => the attribute to be used as activity
        - Parameters.CASE_ID_KEY => the attribute to be used as case ID

    Returns
    ------------------
    dict
        Dictionary associating to each activity the number of cases for which the rework happened
    """
    if parameters is None:
        parameters = {}

    activity_key = exec_utils.get_param_value(
        Parameters.ACTIVITY_KEY, parameters, xes_constants.DEFAULT_NAME_KEY
    )
    case_id_key = exec_utils.get_param_value(
        Parameters.CASE_ID_KEY, parameters, constants.CASE_CONCEPT_NAME
    )

    # Select only needed columns
    selected_lf = lf.select([activity_key, case_id_key])

    # Add cumulative count for each activity within each case
    with_counts = (
        selected_lf
        .with_columns(
            pl.col(activity_key)
            .cum_count()
            .over([case_id_key, activity_key])
            .alias("__rework_count")
        )
    )

    # Filter for rework cases (count > 0, meaning activity occurred more than once)
    rework_cases = with_counts.filter(pl.col("__rework_count") > 1)

    # Get unique activity-case pairs for rework
    unique_rework = rework_cases.select([activity_key, case_id_key]).unique()

    # Count cases with rework per activity
    result_df = unique_rework.group_by(activity_key).len(name="count").collect()

    # Convert to dictionary
    ret = dict(zip(result_df[activity_key].to_list(), result_df["count"].to_list()))

    return ret