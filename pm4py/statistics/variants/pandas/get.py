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
from pm4py.statistics.traces.pandas import case_statistics
from collections import Counter


def get_variants_count(df, parameters=None):
    """
    Gets the dictionary of variants from the current dataframe

    Parameters
    --------------
    df
        Dataframe
    parameters
        Possible parameters of the algorithm, including:
            Parameters.ACTIVITY_KEY -> Column that contains the activity

    Returns
    --------------
    variants_set
        Dictionary of variants in the log
    """
    if parameters is None:
        parameters = {}
    var_stats = case_statistics.get_variant_statistics(df, parameters=parameters)
    if var_stats:
        count_key = list(x for x in var_stats[0].keys() if not x == "variant")[0]
        return {x["variant"]: x[count_key] for x in var_stats}
    return {}


def get_variants_set(df, parameters=None):
    """
    Gets the set of variants from the current dataframe

    Parameters
    --------------
    df
        Dataframe
    parameters
        Possible parameters of the algorithm, including:
            Parameters.ACTIVITY_KEY -> Column that contains the activity

    Returns
    --------------
    variants_set
        Set of variants in the log
    """
    if parameters is None:
        parameters = {}
    var_stats = case_statistics.get_variant_statistics(df, parameters=parameters)
    return set(x["variant"] for x in var_stats)
