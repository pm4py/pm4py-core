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
from pm4py.util import exec_utils, constants
from enum import Enum
import numpy as np
import pandas as pd


class Parameters(Enum):
    INCLUDE_HEADER = "include_header"
    MAX_LEN = "max_len"
    DEBUG = "debug"
    ENABLE_OBJECT_LIFECYCLE_PATHS = "enable_object_lifecycle_paths"


def __transform_to_string(stru: str) -> str:
    if stru.startswith("@@ocel_lif_activity_"):
        return "Number of occurrences of the activity "+stru.split("@@ocel_lif_activity_")[1]
    elif stru.startswith("@@object_lifecycle_unq_act"):
        return "Number of unique activities in the lifecycle of the object"
    elif stru.startswith("@@object_lifecycle_length"):
        return "Number of events in the lifecycle of the object"
    elif stru.startswith("@@object_lifecycle_duration"):
        return "Duration of the lifecycle of the object"
    elif stru.startswith("@@object_lifecycle_start_timestamp"):
        return "Start timestamp of the lifecycle of the object"
    elif stru.startswith("@@object_lifecycle_end_timestamp"):
        return "Completion timestamp of the lifecycle of the object"
    elif stru.startswith("@@object_degree_centrality"):
        return "Degree centrality of the object in the object interaction graph"
    elif stru.startswith("@@object_general_interaction_graph"):
        return "Number of objects related in the object interaction graph"
    elif stru.startswith("@@object_general_descendants_graph_descendants"):
        return "Number of objects which follow the current object in the object descendants graph"
    elif stru.startswith("@@object_general_inheritance_graph_ascendants"):
        return "Number of objects which follow the current object in the object inheritance graph"
    elif stru.startswith("@@object_general_descendants_graph_ascendants"):
        return "Number of objects which precede the current object in the object descendants graph"
    elif stru.startswith("@@object_general_inheritance_graph_descendants"):
        return "Number of objects which precede the current object in the object descendants graph"
    elif stru.startswith("@@object_cobirth"):
        return "Number of objects starting their lifecycle together with the current object"
    elif stru.startswith("@@object_codeath"):
        return "Number of objects ending their lifecycle together with the current object"
    elif stru.startswith("@@object_interaction_graph_"):
        return "Number of object of type "+stru.split("@@object_interaction_graph_")[1]+" related to the current object in the object interaction graph"
    elif stru.startswith("@@ocel_lif_path_"):
        path = stru.split("@@ocel_lif_path_")[1]
        act1 = path.split("##")[0]
        act2 = path.split("##")[1]
        return "Frequency of the path \""+act1+"\" -> \""+act2+"\" in the lifecycle of the object"

    return stru


def textual_abstraction_from_fea_df(fea_df: pd.DataFrame, parameters: Optional[Dict[Any, Any]] = None) -> str:
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
        ret.append("Beforehand, a bit of notions.")
        ret.append("Given an object-centric event log, the object interaction graph connects objects that are related in at least an event.")
        ret.append("The object descendants graph connects objects related in at least an event, when the lifecycle of the second object starts after the lifecycle of the first.")
        ret.append("The object inheritance graph connects objects when there an event that ends the lifecycle of the first object and starts the lifecycle of the second one.")
        ret.append("\n\n")
        ret.append("Given the following features:\n\n")

    ret = " ".join(ret)

    i = 0
    while i < len(cols):
        if len(ret) >= max_len:
            break

        stru = cols[i][0]+":    number of non-zero values: "+str(cols[i][1])+" ; quantiles of the non-zero: "+str(cols[i][3].quantile([0.0, 0.25, 0.5, 0.75, 1.0]).to_dict())+"\n"
        ret = ret + stru

        i = i + 1

    return ret


def apply(ocel: OCEL, obj_type: str, parameters: Optional[Dict[Any, Any]] = None) -> str:
    if parameters is None:
        parameters = {}

    debug = exec_utils.get_param_value(Parameters.DEBUG, parameters, True)
    enable_object_lifecycle_paths = exec_utils.get_param_value(Parameters.ENABLE_OBJECT_LIFECYCLE_PATHS, parameters, False)

    import pm4py

    fea_df = pm4py.extract_ocel_features(ocel, obj_type, include_obj_id=False, debug=debug, enable_object_lifecycle_paths=enable_object_lifecycle_paths)

    return textual_abstraction_from_fea_df(fea_df, parameters=parameters)
