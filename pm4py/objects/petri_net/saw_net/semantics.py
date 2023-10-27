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

import copy
import itertools
import random
from abc import ABC, abstractclassmethod
from collections import Counter
from typing import Counter as TCounter
from typing import Generic, List, Optional, Tuple, TypeVar

from pm4py.objects.petri_net.saw_net.obj import StochasticArcWeightNet
from pm4py.objects.petri_net.stochastic.semantics import \
    StochasticPetriNetSemantics

N = TypeVar("N", bound=StochasticArcWeightNet)
T = TypeVar("T", bound=StochasticArcWeightNet.Transition)
P = TypeVar("P", bound=StochasticArcWeightNet.Place)
A = TypeVar("A", bound=StochasticArcWeightNet.Arc)
B = TypeVar("B", bound=StochasticArcWeightNet.Binding)


class StochasticArcWeightNetSemantics(StochasticPetriNetSemantics[N], Generic[N], ABC):

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
            if marking[a.source] < min([k for k, v in a.weight_distribution.items() if v > 0]):
                return False
        return True

    @classmethod
    def fire(cls, pn: N, binding: B, marking: TCounter[P]) -> TCounter[P]:
        """fires the binding in the given marking. Does not check if the the binding is feasible (this should be handled by the invoking code)

        Args:
            pn (N): saw net to use
            marking (TCounter[P]): marking to use
            binding (B): binding to use

        Returns:
            TCounter[P]: _description_
        """
        m_out = copy.copy(marking)
        for (a, w) in binding:
            if isinstance(a.source, StochasticArcWeightNet.Place):
                m_out[a.source] -= w
            else:
                m_out[a.target] += w
        return m_out

    @classmethod
    def all_legal_bindings(cls, pn: N, transition: T) -> List[List[Tuple[A, int]]]:
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
    def all_enabled_bindings(cls, pn: N, transition: T, marking: TCounter[P]) -> List[List[Tuple[A, int]]]:
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
        return list(filter(lambda b: cls.is_enabled_binding(pn, transition, b, marking), cls.all_legal_bindings(pn, transition)))

    @classmethod
    def is_enabled_binding(cls, pn: N, transition: T, binding: StochasticArcWeightNet.Binding, marking: TCounter[P]) -> bool:
        """
        Checks if the provided binding is enabled

        Parameters
        ----------
        :param pn: Petri net
        :param marking: marking to use
        :param transition: transition to genereate all feasible bindings for        

        Returns
        -------
        :return: bool indicates if the binding is enabled
        """
        if transition not in pn.transitions:
            return False
        places_in_bindings = set(filter(lambda x: isinstance(x, StochasticArcWeightNet.Place), [
                                 x for x in list(itertools.chain(*[(a.source, a.target) for (a, w) in binding]))]))
        for a in transition.in_arcs:
            if a.source not in places_in_bindings:
                return False
        for a in transition.out_arcs:
            if a.target not in places_in_bindings:
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
    def amortized_priority(cls, binding: StochasticArcWeightNet.Binding) -> float:
        """
        Computes the amortized priority (a.k.a weight) of a binding. The amortized priority is equal to the product of all individual weights of the arc weights includec in the binding.

        Args:
            binding (StochasticArcWeightNet.Binding): input binding

        Returns:
            float: amortized weight
        """
        prod = 1
        for (a, w) in binding:
            prod *= a.weight_distribution[w]
        return prod

    @abstractclassmethod
    def probability_of_binding(cls, pn: N, transition: T,  binding: StochasticArcWeightNet.Binding, marking: TCounter[P]) -> float:
        """
        Calculates the probability of firing a transition t under binding b in the net, in the given marking.

        Parameters
        ----------
        :param pn: Petri net        
        :param transition: transition to fire
        :param binding: binding to consider
        :param marking: marking to use

        Returns
        -------
        :return: firing probability of transition t under binding b
        """
        pass


class LocalStochasticArcWeightNetSemantics(StochasticArcWeightNetSemantics[N], Generic[N]):

    @classmethod
    def probability_of_binding(cls, pn: N, transition: T,  binding: StochasticArcWeightNet.Binding, marking: TCounter[P]) -> float:
        """
        Calculates the probability of firing a transition t under binding b in the net, in the given marking.

        Parameters
        ----------
        :param pn: Petri net        
        :param transition: transition to fire
        :param binding: binding to consider
        :param marking: marking to use

        Returns
        -------
        :return: firing probability of transition t under binding b
        """
        s = 0
        for t in pn.transitions:
            if cls.is_enabled(pn,t,marking):
                for b in cls.all_enabled_bindings(pn,transition,marking):
                    s += t.weight * cls.amortized_priority(b)
        
        print(cls.amortized_priority(binding))
        return transition.weight * cls.amortized_priority(binding) / s


class GlobalStochasticArcWeightNetSemantics(StochasticArcWeightNetSemantics[N], Generic[N]):

    @classmethod
    def probability_of_transition(cls, pn: N, transition: T, marking: TCounter[P]) -> float:
        """
        Compute the probability of firing a transition in the net and marking.

        Args:
            pn (N): Stochastic net
            transition (T): transition to fire
            marking (Counter[P]): marking to use

        Returns:
            float: _description_
        """
        return 0.0 if not transition in pn.transitions or not cls.is_enabled(pn, transition, marking) else sum([transition.weight * cls.amortized_priority(b) for b in cls.all_enabled_bindings(pn, transition, marking)]) / sum([t.weight * cls.amortized_priority(b) for t in pn.transitions if cls.is_enabled(pn, t, marking) for b in cls.all_enabled_bindings(pn, t, marking)])

    @classmethod
    def sample_enabled_transition(cls, pn: N, marking: TCounter[P], seed: int = None) -> Optional[Tuple[T, B]]:
        if seed is not None:
            random.seed(seed)
        bindings = list()
        probs = list()
        for t in [t for t in pn.transitions if cls.is_enabled(pn, t, marking)]:
            for b in cls.all_enabled_bindings(pn, t, marking):
                bindings.append((t, b))
                probs.append(cls.probability_of_binding(pn, t, b, marking))
        return None if len(bindings) == 0 else random.choices(bindings, probs)[0]

    @classmethod
    def probability_of_binding(cls, pn: N, transition: T,  binding: StochasticArcWeightNet.Binding, marking: TCounter[P]) -> float:
        """
        Calculates the probability of firing a transition t under binding b in the net, in the given marking.

        Parameters
        ----------
        :param pn: Petri net        
        :param transition: transition to fire
        :param binding: binding to consider
        :param marking: marking to use

        Returns
        -------
        :return: firing probability of transition t under binding b
        """
        return 0.0 if transition not in pn.transitions or not cls.is_enabled_binding(pn, transition, binding, marking) else (transition.weight * cls.amortized_priority(binding)) / sum([t.weight * cls.amortized_priority(b) for t in pn.transitions if cls.is_enabled(pn, t, marking) for b in cls.all_enabled_bindings(pn, t, marking)])
