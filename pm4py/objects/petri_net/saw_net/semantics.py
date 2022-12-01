import itertools
import random
from collections import Counter
from typing import Collection
from typing import Counter as TCounter
from typing import Generic, List, Tuple, TypeVar

from pm4py.objects.petri_net.saw_net.obj import StochasticArcWeightNet
from pm4py.objects.petri_net.semantics import PetriNetSemantics

N = TypeVar("N", bound=StochasticArcWeightNet)
T = TypeVar("T", bound=StochasticArcWeightNet.Transition)
P = TypeVar("P", bound=StochasticArcWeightNet.Place)
A = TypeVar("A", bound=StochasticArcWeightNet.Arc)


class StochasticArcWeightNetSemantics(PetriNetSemantics[N], Generic[N]):

    @classmethod
    def is_enabled(cls, pn: N, transition: T, marking: TCounter[P]) -> bool:
        """
        Checks whether a given transition is enabled in a given Petri net and marking.
        Every place should at least have the same number of tokens as the  minimum binding that has a weight above 0

        Parameters
        ----------
        :param pn: Petri net
        :param transition: transition to check        
        :param marking: marking to check

        Returns
        -------
        :return: true if enabled, false otherwise
        """
        if not transition in pn.transitions:
            return False
        for a in transition.in_arcs:
            for p in a.source:
                if marking[p] < min([k for k, v in a.weight_distribution.itmes() if v > 0]):
                    return False
        return True

    @classmethod
    def all_bindings(cls, pn: N, transition: T) -> List[List[Tuple[A, int]]]:
        """
        Creates all possible bindings for a given input transition

        Parameters
        ----------
        :param pn: Petri net
        :param transition: transition to genereate all bindings for        

        Returns
        -------
        :return: list containing all posible bindings
        """
        if transition not in pn.transitions:
            return []
        else:
            l = list()
            for a in transition.in_arcs:
                l.append([(a, k) for k, v in a.weight_distribution.items()
                         if v > 0])
            for a in transition.out_arcs:
                l.append([(a, k)
                         for k, v in a.weight_distribution.items() if v > 0])
            return list(itertools.product(*l))

    @classmethod
    def all_feasible_bindings(cls, pn: N, transition: T, marking: TCounter[P]) -> List[List[Tuple[A, int]]]:
        """
        Creates all possible feasible bindings for a given input transition in a given marking

        Parameters
        ----------
        :param pn: Petri net
        :param marking: marking to use
        :param transition: transition to genereate all feasible bindings for        

        Returns
        -------
        :return: list containing all posible feasible bindings
        """
        return list(filter(lambda b: StochasticArcWeightNetSemantics.is_feasible_binding(pn, transition, b, marking), StochasticArcWeightNetSemantics.all_bindings(pn, transition)))

    @classmethod
    def is_feasible_binding(cls, pn: N, transition: T, binding: StochasticArcWeightNet.Binding, marking: TCounter[P]) -> bool:
        """
        Creates all possible feasible bindings for a given input transition in a given marking

        Parameters
        ----------
        :param pn: Petri net
        :param marking: marking to use
        :param transition: transition to genereate all feasible bindings for        

        Returns
        -------
        :return: list containing all posible feasible bindings
        """
        if transition not in pn.transitions:
            return False
        for (a, w) in binding:
            if a.weight_distribution[w] == 0.0:
                return False
            if transition not in {a.source, a.target}:
                return False
            if transition == a.target:
                if w > marking[a.source]:
                    return False
        return True

    @classmethod
    def probability_of_binding(cls, pn: N, transition: T,  binding: StochasticArcWeightNet.Binding, marking: TCounter[P]) -> float:
        if transition not in pn.transitions or not StochasticArcWeightNetSemantics.is_feasible_binding(pn, transition, binding, marking):
            return 0.0
