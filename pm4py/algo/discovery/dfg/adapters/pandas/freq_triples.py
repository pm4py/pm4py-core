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
from pm4py.util import constants, pandas_utils

def get_freq_triples(df, activity_key="concept:name", case_id_glue="case:concept:name", timestamp_key="time:timestamp",
                     sort_caseid_required=True, sort_timestamp_along_case_id=True):
    """
    Gets the frequency triples out of a dataframe

    Parameters
    ------------
    df
        Dataframe
    activity_key
        Activity key
    case_id_glue
        Case ID glue
    timestamp_key
        Timestamp key
    sort_caseid_required
        Determine if sort by case ID is required (default: True)
    sort_timestamp_along_case_id
        Determine if sort by timestamp is required (default: True)

    Returns
    -------------
    freq_triples
        Frequency triples from the dataframe
    """
    import pandas as pd

    if sort_caseid_required:
        if sort_timestamp_along_case_id:
            df = df.sort_values([case_id_glue, timestamp_key])
        else:
            df = df.sort_values(case_id_glue)
    df_reduced = df[[case_id_glue, activity_key]]
    # shift the dataframe by 1
    df_reduced_1 = df_reduced.shift(-1)
    # shift the dataframe by 2
    df_reduced_2 = df_reduced.shift(-2)
    # change column names to shifted dataframe
    df_reduced_1.columns = [str(col) + '_2' for col in df_reduced_1.columns]
    df_reduced_2.columns = [str(col) + '_3' for col in df_reduced_2.columns]

    df_successive_rows = pandas_utils.concat([df_reduced, df_reduced_1, df_reduced_2], axis=1)
    df_successive_rows = df_successive_rows[df_successive_rows[case_id_glue] == df_successive_rows[case_id_glue + '_2']]
    df_successive_rows = df_successive_rows[df_successive_rows[case_id_glue] == df_successive_rows[case_id_glue + '_3']]
    all_columns = set(df_successive_rows.columns)
    all_columns = list(all_columns - set([activity_key, activity_key + '_2', activity_key + '_3']))
    directly_follows_grouping = df_successive_rows.groupby([activity_key, activity_key + '_2', activity_key + '_3'])
    if all_columns:
        directly_follows_grouping = directly_follows_grouping[all_columns[0]]
    freq_triples = directly_follows_grouping.size().to_dict()
    return freq_triples
