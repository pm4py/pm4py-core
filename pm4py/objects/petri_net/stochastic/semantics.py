import random
from typing import Collection, Counter, Generic, TypeVar

from pm4py.objects.petri_net.semantics import PetriNetSemantics
from pm4py.objects.petri_net.stochastic.obj import StochasticPetriNet

N = TypeVar("N", bound=StochasticPetriNet)
T = TypeVar("T", bound=StochasticPetriNet.Transition)
P = TypeVar("P", bound=StochasticPetriNet.Place)


class StochasticPetriNetSemantics(PetriNetSemantics[N], Generic[N]):

    @classmethod
    def sample_enabled_transition(cls, pn: N, marking: Counter[P], seed: int = None) -> T:
        """
        Randomly samples a transition from all enabled transitions

        Parameters
        ----------
        :param pn: Petri net    
        :param marking: marking to use

        Returns
        -------
        :return: a transition sampled from the enabled transitions
        """
        if seed is not None:
            random.seed(seed)
        enabled = list(filter(lambda t: cls.is_enabled(
            pn, t, marking), [t for t in pn.transitions]))
        weights = list(map(lambda t: t.weight, enabled))
        # sum_weights = sum(weights)
        # probs = list(map(lambda w: w/sum_weights, weights))
        return random.choices(enabled, weights)[0]
