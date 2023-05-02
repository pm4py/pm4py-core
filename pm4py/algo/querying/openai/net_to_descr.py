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
