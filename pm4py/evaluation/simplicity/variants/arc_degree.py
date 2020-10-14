from statistics import mean
from enum import Enum
from pm4py.util import exec_utils


class Parameters(Enum):
    K = "k"


def apply(petri_net, parameters=None):
    """
    Gets simplicity from a Petri net

    Vázquez-Barreiros, Borja, Manuel Mucientes, and Manuel Lama. "ProDiGen: Mining complete, precise and minimal
    structure process models with a genetic algorithm." Information Sciences 294 (2015): 315-333.

    Parameters
    -----------
    petri_net
        Petri net
    parameters
        Possible parameters of the algorithm:
            - K: defines the value to be substracted in the formula: the lower is the value,
            the lower is the simplicity value. k is the baseline arc degree (that is subtracted from the others)

    Returns
    -----------
    simplicity
        Simplicity measure associated to the Petri net
    """
    if parameters is None:
        parameters = {}

    # original model: we have plenty of choices there.
    # one choice is about taking a model containing the most frequent variant,
    # along with a short circuit between the final and the initial marking.
    # in that case, the average arc degree of the "original model" is 2

    # keep the default to 2
    k = exec_utils.get_param_value(Parameters.K, parameters, 2)

    # TODO: verify the real provenence of the approach before!

    all_arc_degrees = []
    for place in petri_net.places:
        all_arc_degrees.append(len(place.in_arcs) + len(place.out_arcs))
    for trans in petri_net.transitions:
        all_arc_degrees.append(len(trans.in_arcs) + len(trans.out_arcs))

    mean_degree = mean(all_arc_degrees) if all_arc_degrees else 0.0

    simplicity = 1.0 / (1.0 + max(mean_degree - k, 0))

    return simplicity
