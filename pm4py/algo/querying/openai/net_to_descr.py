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

from typing import Optional, Dict, Any
from pm4py.objects.petri_net.obj import PetriNet, Marking
from enum import Enum
from pm4py.util import exec_utils


class Parameters(Enum):
    RESPONSE_HEADER = "response_header"


def apply(net: PetriNet, im: Marking, fm: Marking, parameters: Optional[Dict[Any, Any]] = None) -> str:
    """
    Provides the description of an accepting Petri net

    Parameters
    --------------
    net
        Petri net
    im
        Initial marking
    fm
        Final marking
    parameters
        Possible parameters of the algorithm, including:
        - Parameters.INCLUDE_HEADER => includes the header

    Returns
    --------------
    stru
        String representation of the given accepting Petri net
    """
    if parameters is None:
        parameters = {}

    include_header = exec_utils.get_param_value(Parameters.RESPONSE_HEADER, parameters, True)

    ret = ["\n"]
    if include_header:
        ret.append("If I have a Petri net:\n")
    ret.append(repr(net))
    ret.append("\ninitial marking: "+repr(im))
    ret.append("final marking: "+repr(fm))
    ret.append("\n")

    return "\n".join(ret)
