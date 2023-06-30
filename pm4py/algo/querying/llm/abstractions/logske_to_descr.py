from enum import Enum
from typing import Optional, Dict, Any
from pm4py.util import exec_utils


class Parameters(Enum):
    INCLUDE_HEADER = "include_header"


def apply(lsk: Dict[str, Any], parameters: Optional[Dict[Any, Any]] = None) -> str:
    if parameters is None:
        parameters = {}

    include_header = exec_utils.get_param_value(Parameters.INCLUDE_HEADER, parameters, True)

    ret = ["\n"]

    if include_header:
        ret.append("If I have the following declarative constraints:\n\n")

    # equivalence
    ret.append("Equivalence (if the first activity occurs, then it has the same occurrences as the second one): ")
    for constr in lsk["equivalence"]:
        ret.append(" " + str(constr))
    ret.append("\n\n")

    # always before
    ret.append("Always Before (if the first activity occur, then the second activity should have been executed previously): ")
    for constr in lsk["always_before"]:
        ret.append(" " + str(constr))
    ret.append("\n\n")

    # always after
    ret.append("Always After (if the first activity occur, then the second activity is executed in one of the following events): ")
    for constr in lsk["always_after"]:
        ret.append(" " + str(constr))
    ret.append("\n\n")

    # never together
    ret.append("Never Together (the two activities cannot co-exist inside the same case): ")
    for constr in lsk["never_together"]:
        ret.append(" " + str(constr))
    ret.append("\n\n")

    # activity occurrences
    ret.append("Activity Occurrences (bounds the number of occurrences for an activity in a case): ")
    for constr, occs in lsk["activ_freq"].items():
        ret.append(" " + str(constr) + ": " + ", ".join(sorted([str(x) for x in occs])) + ";")
    ret.append("\n\n")

    # directly-follows
    ret.append("Directly-Follows Constraints (if the first activity occurs, then the second activity shall occur immediately after): ")
    for constr in lsk["directly_follows"]:
        ret.append(" "+str(constr))
    ret.append("\n\n")

    return "".join(ret)

