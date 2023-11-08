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

import random
from typing import Counter, Generic, TypeVar

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
        weights = list(map(lambda t : cls.probability_of_transition(pn,t,marking), enabled))
        return random.choices(enabled, weights)[0]

    @classmethod
    def probability_of_transition(cls, pn: N, transition: T, marking: Counter[P]) -> float:
        """
        Compute the probability of firing a transition in the net and marking.

        Args:
            pn (N): Stochastic net
            transition (T): transition to fire
            marking (Counter[P]): marking to use

        Returns:
            float: _description_
        """
        if not transition in pn.transitions or not cls.is_enabled(pn, transition, marking):
            return 0.0
        return transition.weight / sum(list(map(lambda t: t.weight, list(filter(lambda t: cls.is_enabled(pn, t, marking), [t for t in pn.transitions])))))
