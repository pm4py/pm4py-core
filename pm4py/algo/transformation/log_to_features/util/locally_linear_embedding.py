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
import math
from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any, Tuple, List

import numpy as np
from pm4py.util import ml_utils

from pm4py.objects.conversion.log import converter as log_converter
from pm4py.objects.log.obj import EventLog
from pm4py.algo.transformation.log_to_features import algorithm as log_to_features
from pm4py.objects.log.util import sorting
from pm4py.util import constants, xes_constants
from pm4py.util import exec_utils, pandas_utils


class Parameters(Enum):
    ACTIVITY_KEY = constants.PARAMETER_CONSTANT_ACTIVITY_KEY
    TIMESTAMP_KEY = constants.PARAMETER_CONSTANT_TIMESTAMP_KEY
    CASE_ID_KEY = constants.PARAMETER_CONSTANT_CASEID_KEY


def smooth(y: np.ndarray, box_pts: int) -> np.ndarray:
    """
    Smooths the points in y with a weighted average.

    Parameters
    ----------------
    y
        Points
    box_pts
        Size of the weighted average

    Returns
    ----------------
    y_smooth
        Smoothened y
    """
    box = np.ones(box_pts) / box_pts
    y_smooth = np.convolve(y, box, mode='same')
    return y_smooth


def apply(log: EventLog, parameters: Optional[Dict[str, Any]] = None) -> Tuple[List[datetime], np.ndarray]:
    """
    Analyse the evolution of the features over the time using a locally linear embedding.

    Parameters
    -----------------
    log
        Event log
    parameters
        Variant-specific parameters, including:
        - Parameters.ACTIVITY_KEY => the activity key
        - Parameters.TIMESTAMP_KEY => the timestamp key
        - Parameters.CASE_ID_KEY => the case ID key

    Returns
    ----------------
    x
        Date attributes (starting points of the cases)
    y
        Deviation from the standard behavior (higher absolute values of y signal a higher deviation
        from the standard behavior)
    """
    if parameters is None:
        parameters = {}

    activity_key = exec_utils.get_param_value(Parameters.ACTIVITY_KEY, parameters, xes_constants.DEFAULT_NAME_KEY)
    timestamp_key = exec_utils.get_param_value(Parameters.TIMESTAMP_KEY, parameters,
                                               xes_constants.DEFAULT_TIMESTAMP_KEY)

    if pandas_utils.check_is_pandas_dataframe(log):
        # keep only the needed columns
        case_id_key = exec_utils.get_param_value(Parameters.CASE_ID_KEY, parameters, constants.CASE_CONCEPT_NAME)
        log = log[[case_id_key, activity_key, timestamp_key]]

    log = log_converter.apply(log, variant=log_converter.Variants.TO_EVENT_LOG, parameters=parameters)
    log = sorting.sort_timestamp(log, timestamp_key)

    x = [trace[0][timestamp_key] for trace in log]
    data, feature_names = log_to_features.apply(log, parameters={"str_ev_attr": [activity_key], "str_evsucc_attr": [activity_key]})
    data = np.array([np.array(x) for x in data])

    tsne = ml_utils.LocallyLinearEmbedding(n_components=1, eigen_solver='dense')
    data = tsne.fit_transform(data)
    data = np.ndarray.flatten(data)

    y = data
    smooth_amount = 1 + math.floor(math.sqrt(len(y)))
    y = smooth(y, smooth_amount)

    return x, y
