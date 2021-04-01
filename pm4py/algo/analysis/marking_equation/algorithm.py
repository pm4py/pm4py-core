from enum import Enum
from typing import Optional, Dict, Any

from pm4py.algo.analysis.marking_equation.variants import classic
from pm4py.objects.petri.obj import PetriNet, Marking
from pm4py.util import exec_utils


class Variants(Enum):
    CLASSIC = classic


def build(net: PetriNet, im: Marking, fm: Marking, variant=Variants.CLASSIC,
          parameters: Optional[Dict[Any, Any]] = None) -> Any:
    """
    Builds the marking equation out of a Petri net

    Parameters
    ---------------
    net
        Petri net
    im
        Initial marking
    fm
        Final marking
    variant
        Variant of the algorithm to use, possible values:
        - Variants.CLASSIC
    parameters
        Parameters of the algorithm, including:
        - Parameters.CASE_ID_KEY => attribute to use as case identifier
        - Parameters.ACTIVITY_KEY => attribute to use as activity
        - Parameters.COSTS => (if provided) the cost function (otherwise the default cost function is applied)
        - Parameters.INCIDENCE_MATRIX => (if provided) the incidence matrix of the Petri net
        - Parameters.A => (if provided) the A numpy matrix of the incidence matrix
        - Parameters.FULL_BOOTSTRAP_REQUIRED => The preset/postset of places/transitions need to be inserted
    """
    return exec_utils.get_variant(variant).build(net, im, fm, parameters=parameters)


def get_h_value(solver: Any, variant=Variants.CLASSIC, parameters: Optional[Dict[Any, Any]] = None) -> int:
    """
    Gets the heuristics value from the marking equation

    Parameters
    --------------
    solver
        Marking equation solver (class in this file)
    variant
        Variant of the algorithm to use, possible values:
        - Variants.CLASSIC
    parameters
        Possible parameters of the algorithm
    """
    return exec_utils.get_variant(variant).get_h_value(solver, parameters=parameters)
