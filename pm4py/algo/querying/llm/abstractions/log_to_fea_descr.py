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

from typing import Optional, Dict, Any, Union
from pm4py.util import exec_utils, constants, pandas_utils
from pm4py.objects.log.obj import EventLog, EventStream
import pandas as pd
from pm4py.objects.conversion.log import converter as log_converter
from pm4py.algo.transformation.log_to_features import algorithm as log_to_features
from enum import Enum
import numpy as np


class Parameters(Enum):
    INCLUDE_HEADER = "include_header"
    MAX_LEN = "max_len"


def __transform_to_string(stru: str) -> str:
    if stru == "@@max_concurrent_activities_general":
        return "Maximum Number of Concurrent Events"
    elif stru.startswith("@@max_concurrent_activities_like_"):
        return "Maximum Number of Concurrent '"+stru.split("@@max_concurrent_activities_like_")[-1]+"'"
    elif stru.startswith("event:"):
        stru = stru.split("event:")[-1]
        if "@" in stru:
            attr = stru.split("@")[0]
            value = stru.split("@")[-1]
            return "Value '"+value+"' for Event Attribute '"+attr+"'"
        else:
            return "Values for Event Attribute '"+stru+"'"
    elif stru.startswith("trace:"):
        stru = stru.split("trace:")[-1]
        if "@" in stru:
            attr = stru.split("@")[0]
            value = stru.split("@")[-1]
            return "Value '"+value+"' for Case Attribute '"+attr+"'"
        else:
            return "Values for Case Attribute '"+stru+"'"
    elif stru.startswith("succession:"):
        stru = stru.split("succession:")[-1]
        attr = stru.split("@")[0]
        stru = stru.split("@")[-1]
        val1 = stru.split("#")[0]
        val2 = stru.split("#")[-1]
        return "Succession '"+val1+"' -> '"+val2+"' for the Values of the Attribute '"+attr+"'"
    elif stru == "@@caseDuration":
        return "Case Duration"
    elif stru.startswith("firstIndexAct@@"):
        return "First Position of the Activity '"+stru.split("@@")[-1]+"' in the Case"
    elif stru.startswith("lastIndexAct@@"):
        return "Last Position of the Activity '"+stru.split("@@")[-1]+"' in the Case"
    elif stru.startswith("startToLastOcc@@"):
        return "Time from Case Start to Last Occurrence of the Activity '" + stru.split("@@")[-1] + "'"
    elif stru.startswith("lastOccToEnd@@"):
        return "Time from Last Occurrence of the Activity '" + stru.split("@@")[-1] + "' to Case End"
    elif stru.startswith("startToFirstOcc@@"):
        return "Time from Case Start to First Occurrence of the Activity '"+stru.split("@@")[-1]+"'"
    elif stru.startswith("firstOccToEnd@@"):
        return "Time from First Occurrence of the Activity '"+stru.split("@@")[-1]+"' to Case End"
    elif stru.startswith("directPathPerformanceLastOcc@@"):
        stru = stru.split("@@")[-1].split("##")
        return "Directly-Follows Paths Throughput between '" + stru[0] + "' and '" + stru[1] + "' (last occurrence of the path in the case)"
    elif stru.startswith("indirectPathPerformanceLastOcc@@"):
        stru = stru.split("@@")[-1].split("##")
        return "Eventually-Follows Paths Throughput between '" + stru[0] + "' and '" + stru[1] + "' (last occurrence of the path in the case)"
    elif stru.startswith("resource_workload@@"):
        return "Resource Workload of '"+stru.split("@@")[-1]+"'"
    elif stru == "@@work_in_progress":
        return "Work in Progress"

    return stru


def textual_abstraction_from_fea_df(fea_df: pd.DataFrame, parameters: Optional[Dict[Any, Any]] = None) -> str:
    """
    Returns the textual abstraction of ML features already encoded in a feature table

    Minimum viable example:

        import pm4py
        from pm4py.algo.querying.llm.abstractions import log_to_fea_descr

        log = pm4py.read_xes("tests/input_data/receipt.xes", return_legacy_log_object=True)
        fea_df = pm4py.extract_features_dataframe(log)
        text_abstr = log_to_fea_descr.textual_abstraction_from_fea_df(fea_df)
        print(text_abstr)

    Parameters
    ---------------
    fea_df
        Feature table (numeric features; stored as Pandas dataframe)
    parameters
        Parameters that should be provided to the feature extraction, plus:
        - Parameters.INCLUDE_HEADER => includes a descriptive header in the returned text
        - Parameters.MAX_LEN => maximum length of the provided text (if necessary, only the most meaningful features are kept)

    Returns
    ---------------
    stru
        Textual abstraction
    """
    if parameters is None:
        parameters = {}

    include_header = exec_utils.get_param_value(Parameters.INCLUDE_HEADER, parameters, True)
    max_len = exec_utils.get_param_value(Parameters.MAX_LEN, parameters, constants.OPENAI_MAX_LEN)

    cols = []

    for c in fea_df.columns:
        ser = fea_df[c]
        ser1 = ser[ser > 0]
        if len(ser1) > 0:
            desc = __transform_to_string(c)
            avg = np.average(ser1)
            stdavg = 0 if avg == 0 or len(ser1) == 1 else np.std(ser1)/avg
            cols.append([desc, len(ser1), stdavg, ser1])

    cols = sorted(cols, key=lambda x: (x[1], x[2], x[0]), reverse=True)

    ret = ["\n"]

    if include_header:
        ret.append("Given the following features:\n\n")

    ret = " ".join(ret)

    i = 0
    while i < len(cols):
        if len(ret) >= max_len:
            break

        fea_name = cols[i][0]
        fea_col = cols[i][3]

        stru = fea_name+":    number of non-zero values: "+str(cols[i][1])+" ; quantiles of the non-zero: "+str(fea_col.quantile([0.0, 0.25, 0.5, 0.75, 1.0]).to_dict())+"\n"

        ret = ret + stru

        i = i + 1

    return ret


def apply(log: Union[EventLog, EventStream, pd.DataFrame], parameters: Optional[Dict[Any, Any]] = None) -> str:
    """
    Returns the textual abstraction of ML features extracted from a traditional event log object.

    Minimum viable example:

        import pm4py
        from pm4py.algo.querying.llm.abstractions import log_to_fea_descr

        log = pm4py.read_xes("tests/input_data/receipt.xes", return_legacy_log_object=True)
        text_abstr = log_to_fea_descr.apply(log)
        print(text_abstr)

    Parameters
    ---------------
    log
        Event log / Pandas dataframe
    parameters
        Parameters that should be provided to the feature extraction, plus:
        - Parameters.INCLUDE_HEADER => includes a descriptive header in the returned text
        - Parameters.MAX_LEN => maximum length of the provided text (if necessary, only the most meaningful features are kept)

    Returns
    ---------------
    stru
        Textual abstraction
    """
    if parameters is None:
        parameters = {}

    log = log_converter.apply(log, variant=log_converter.Variants.TO_EVENT_LOG, parameters=parameters)

    data, feature_names = log_to_features.apply(log, parameters=parameters)

    fea_df = pandas_utils.instantiate_dataframe(data, columns=feature_names)

    return textual_abstraction_from_fea_df(fea_df, parameters=parameters)
