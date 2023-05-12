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
from copy import deepcopy
from enum import Enum
from typing import List, Dict, Any, Optional, Union

from pm4py.objects.log.obj import EventLog
from pm4py.objects.petri_net.utils import align_utils
from pm4py.util import exec_utils


class Parameters(Enum):
    TARGET_ATTRIBUTE = "target_attribute"
    ENABLE_DEEPCOPY = "enable_deepcopy"


def apply(log: EventLog, aligned_traces: List[Dict[str, Any]], parameters: Optional[Dict[Union[str, Parameters], Any]] = None) -> EventLog:
    """
    Enriches a log with the results of the alignment against a model,
    obtained with the parameter 'ret_tuple_as_trans_desc' set to True
    (so the identifiers of the transitions of the model are known).
    In particular, the events that are not move-on-log are enriched with
    the identifier of the corresponding element of the model.

    Parameters
    ----------------
    log
        Event log
    aligned_traces
        Result of the alignments, done with the parameter 'ret_tuple_as_trans_Desc_ set to True.
    parameters
        Parameters of the algorithm:
        - Parameters.TARGET_ATTRIBUTE: attribute that should be used for the enrichment
        - Parameters.ENABLE_DEEPCOPY: deepcopy the event log to not enrich the original log.

    Returns
    ----------------
    enriched_log
        Log enriched with an additional attribute (the identifier of the corresponding element of the model)
    """
    if parameters is None:
        parameters = {}

    target_attribute = exec_utils.get_param_value(Parameters.TARGET_ATTRIBUTE, parameters, "@@transition_id")
    enable_deepcopy = exec_utils.get_param_value(Parameters.ENABLE_DEEPCOPY, parameters, False)

    if enable_deepcopy:
        log = deepcopy(log)

    for i in range(len(aligned_traces)):
        z = 0
        for j in range(len(aligned_traces[i]['alignment'])):
            id_piece = aligned_traces[i]['alignment'][j][0]
            if id_piece[0] != align_utils.SKIP:
                if id_piece[1] != align_utils.SKIP:
                    log[i][z][target_attribute] = id_piece[1]
                z = z + 1

    return log
