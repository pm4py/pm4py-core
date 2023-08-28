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

from enum import Enum
from typing import Optional, Dict, Any
from pm4py.algo.discovery.declare.templates import *
from pm4py.util import exec_utils


class Parameters(Enum):
    INCLUDE_HEADER = "include_header"


def apply(declare: Dict[str, Dict[Any, Dict[str, int]]], parameters: Optional[Dict[Any, Any]] = None) -> str:
    """
    Gets a textual abstraction of a DECLARE model

    Parameters
    ---------------
    declare
        DECLARE model
    parameters
        Possible parameters of the algorithm, including:
        - Parameters.INCLUDE_HEADER => include the header of the response

    Returns
    ---------------
    stru
        Textual abstraction
    """
    if parameters is None:
        parameters = {}

    include_header = exec_utils.get_param_value(Parameters.INCLUDE_HEADER, parameters, True)

    ret = ["\n"]

    if include_header:
        ret.append(
            "I have a DECLARE declarative process model containing the following constraints (here we provide a short explanation):\n")
        ret.append("Existence: the activity is executed at least once.\n")
        ret.append("Absence: the activity is not executed.\n")
        ret.append("Exactly 1: the activity is executed exactly one time.\n")
        ret.append("Initialization: the trace starts with one of the given activities.\n")
        ret.append("Responded existence: given a couple of activities (A, B), if A occurs then B also occurs.\n")
        ret.append("Co-Existence: given a couple of activities (A, B), if A occurs then B also occurs.\n")
        ret.append(
            "Response: given a couple of activities (A, B), if A occurs then B also occurs in the future of the trace.\n")
        ret.append(
            "Precedence: given a couple of activities (A, B), if B occurs then also A occurs in the past of the trace.\n")
        ret.append(
            "Succession: given a couple of activities (A, B), both the response and precedence constraints are satisfied.\n")
        ret.append(
            "Alternate response, alternate precedence, alternate succession: as the constraints mentioned above, but strenghtened by specifying that the events must alternate without repetitions.\n")
        ret.append(
            "Chain response, chain precedence, chain succession: as the constraints mentioned above, strenghtened by imposing the directly-follows relation.\n")
        ret.append("Non Co-Existence: given a couple of activities (A, B), if A occurs then B should not occur.\n")
        ret.append(
            "Non Succession and non Chain succession: given a couple of activities (A, B), B should not follow A.\n")
        ret.append("\n\n")

    ret.append("These are the constraints of the model:\n")
    mapping = {EXISTENCE: "Existence", ABSENCE: "Absence", EXACTLY_ONE: "Exactly 1", INIT: "Initialization",
               RESPONDED_EXISTENCE: "Responded Existence", COEXISTENCE: "Co-Existence", RESPONSE: "Response",
               PRECEDENCE: "Precedence", SUCCESSION: "Succession", ALTRESPONSE: "Alternate response",
               ALTPRECEDENCE: "Alternate precedence", ALTSUCCESSION: "Alternate succession",
               CHAINRESPONSE: "Chain response", CHAINPRECEDENCE: "Chain precedence",
               CHAINSUCCESSION: "Chain succession", NONCOEXISTENCE: "Non Co-Existence", NONSUCCESSION: "Non Succession",
               NONCHAINSUCCESSION: "Non Chain succession"}

    for temp in declare:
        ret.append(mapping[temp] + ": " + ", ".join([str(x) for x in declare[temp]]) + "\n")

    return "".join(ret)
