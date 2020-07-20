from pm4py.simulation.playout.versions import basic_playout, extensive, stochastic_playout
from pm4py.util import exec_utils
from enum import Enum


class Variants(Enum):
    BASIC_PLAYOUT = basic_playout
    STOCHASTIC_PLAYOUT = stochastic_playout
    EXTENSIVE = extensive


DEFAULT_VARIANT = Variants.BASIC_PLAYOUT
VERSIONS = {Variants.BASIC_PLAYOUT, Variants.EXTENSIVE, Variants.STOCHASTIC_PLAYOUT}


def apply(net, initial_marking, final_marking=None, parameters=None, variant=DEFAULT_VARIANT):
    """
    Do the playout of a Petrinet generating a log

    Parameters
    -----------
    net
        Petri net to play-out
    initial_marking
        Initial marking of the Petri net
    final_marking
        (if provided) Final marking of the Petri net
    parameters
        Parameters of the algorithm
    variant
        Variant of the algorithm to use:
            - Variants.BASIC_PLAYOUT: selects random traces from the model, without looking at the
            frequency of the transitions
            - Variants.STOCHASTIC_PLAYOUT: selects random traces from the model, looking at the
            stochastic frequency of the transitions. Requires the provision of the stochastic map
            or the log.
            - Variants.EXTENSIVE: gets all the traces from the model. can be expensive
    """
    return exec_utils.get_variant(variant).apply(net, initial_marking, final_marking=final_marking,
                                                 parameters=parameters)
