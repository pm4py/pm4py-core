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
from collections import Counter
from math import sqrt

from pm4py.algo.conformance.tokenreplay import algorithm as token_replay
from enum import Enum
from pm4py.util import constants
from typing import Optional, Dict, Any, Union
from pm4py.objects.log.obj import EventLog
from pm4py.objects.petri_net.obj import PetriNet, Marking
import pandas as pd


class Parameters(Enum):
    ACTIVITY_KEY = constants.PARAMETER_CONSTANT_ACTIVITY_KEY


def get_generalization(petri_net, aligned_traces):
    trans_occ_map = Counter()
    for trace in aligned_traces:
        for trans in trace["activated_transitions"]:
            trans_occ_map[trans] += 1
    inv_sq_occ_sum = 0.0
    for trans in trans_occ_map:
        this_term = 1.0 / sqrt(trans_occ_map[trans])
        inv_sq_occ_sum = inv_sq_occ_sum + this_term
    for trans in petri_net.transitions:
        if trans not in trans_occ_map:
            inv_sq_occ_sum = inv_sq_occ_sum + 1
    generalization = 1.0
    if len(petri_net.transitions) > 0:
        generalization = 1.0 - inv_sq_occ_sum / float(len(petri_net.transitions))
    return generalization


def apply(log: Union[EventLog, pd.DataFrame], petri_net: PetriNet, initial_marking: Marking, final_marking: Marking, parameters: Optional[Dict[Union[str, Parameters], Any]] = None):
    if parameters is None:
        parameters = {}

    aligned_traces = token_replay.apply(log, petri_net, initial_marking, final_marking, parameters=parameters)

    return get_generalization(petri_net, aligned_traces)
