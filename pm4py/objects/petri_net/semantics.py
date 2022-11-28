import copy
from typing import Counter, Generic, TypeVar

import deprecation

from pm4py.objects.petri_net.obj import PetriNet, Marking
from pm4py.objects.petri_net.sem_interface import Semantics

N = TypeVar("N", bound=PetriNet)
T = TypeVar("T", bound=PetriNet.Transition)
P = TypeVar("P", bound=PetriNet.Place)


class PetriNetSemantics(Generic[N]):

    @classmethod
    def is_enabled(cls, pn: N, transition: T, marking: Counter[P]) -> bool:
        """
        Checks whether a given transition is enabled in a given Petri net and marking

        Parameters
        ----------
        :param pn: Petri net
        :param transition: transition to check        
        :param marking: marking to check

        Returns
        -------
        :return: true if enabled, false otherwise
        """
        if transition not in pn.transitions:
            return False
        else:
            for a in transition.in_arcs:
                if marking[a.source] < a.weight:
                    return False
        return True

    @classmethod
    def fire(cls, pn: N, transition: T, marking: Counter[P]) -> Counter[P]:
        """
        Execute a transition
        For performance reasons, the algorithm method not check if the transition is enabled, i.e., this should be performed by the invoking algorithm (if needed). Hence, markings can become negative. 

        Parameters
        ----------
        :param pn: Petri net
        :param transition: transition to execute        
        :param marking: marking to use

        Returns
        -------
        :return: newly reached marking 
        """
        m_out = copy.copy(marking)
        for a in transition.in_arcs:
            m_out[a.source] -= a.weight
        for a in transition.out_arcs:
            m_out[a.target] += a.weight
        return m_out

class ClassicSemantics(Semantics):
    @deprecation.deprecated("2.3.0", "3.0.0", details="this method will be removed, use PetriNetSemantics.is_enabled() instead")
    def is_enabled(self, t, pn, m, **kwargs):
        """
        Verifies whether a given transition is enabled in a given Petri net and marking

        Parameters
        ----------
        :param t: transition to check
        :param pn: Petri net
        :param m: marking to check

        Returns
        -------
        :return: true if enabled, false otherwise
        """
        return is_enabled(t, pn, m)

    @deprecation.deprecated("2.3.0", "3.0.0", details="this method will be removed, use PetriNetSemantics.fire() instead")
    def execute(self, t, pn, m, **kwargs):
        """
        Executes a given transition in a given Petri net and Marking

        Parameters
        ----------
        :param t: transition to execute
        :param pn: Petri net
        :param m: marking to use

        Returns
        -------
        :return: newly reached marking if :param t: is enabled, None otherwise
        """
        return execute(t, pn, m)

    @deprecation.deprecated("2.3.0", "3.0.0", details="this method will be removed, use PetriNetSemantics.fire() instead")
    def weak_execute(self, t, pn, m, **kwargs):
        """
        Execute a transition even if it is not fully enabled

        Parameters
        ----------
        :param t: transition to execute
        :param pn: Petri net
        :param m: marking to use

        Returns
        -------
        :return: newly reached marking if :param t: is enabled, None otherwise
        """
        return weak_execute(t, m)


    @deprecation.deprecated("2.3.0", "3.0.0", details="this method will be removed")
    def enabled_transitions(self, pn, m, **kwargs):
        """
            Returns a set of enabled transitions in a Petri net and given marking

            Parameters
            ----------
            :param pn: Petri net
            :param m: marking of the pn

            Returns
            -------
            :return: set of enabled transitions
            """
        return enabled_transitions(pn, m)


# 29/08/2021: the following methods have been encapsulated in the ClassicSemantics class.
# the long term idea is to remove them. However, first we need to adapt the existing code to the new
# structure. Moreover, for performance reason, it is better to leave the code here, without having
# to instantiate a ClassicSemantics object.
@deprecation.deprecated("2.3.0", "3.0.0", details="this method will be removed, use PetriNetSemantics.is_enabled() instead")
def is_enabled(t, pn, m):
    if t not in pn.transitions:
        return False
    else:
        for a in t.in_arcs:
            if m[a.source] < a.weight:
                return False
    return True


@deprecation.deprecated("2.3.0", "3.0.0", details="this method will be removed, use PetriNetSemantics.fire() instead")
def execute(t, pn, m):
    if not is_enabled(t, pn, m):
        return None

    m_out = copy.copy(m)
    for a in t.in_arcs:
        m_out[a.source] -= a.weight
        if m_out[a.source] == 0:
            del m_out[a.source]

    for a in t.out_arcs:
        m_out[a.target] += a.weight

    return m_out


@deprecation.deprecated("2.3.0", "3.0.0", details="this method will be removed, use PetriNetSemantics.fire() instead")
def weak_execute(t, m):
    m_out = copy.copy(m)
    for a in t.in_arcs:
        m_out[a.source] -= a.weight
        if m_out[a.source] <= 0:
            del m_out[a.source]
    for a in t.out_arcs:
        m_out[a.target] += a.weight
    return m_out


@deprecation.deprecated("2.3.0", "3.0.0", details="this method will be removed")
def enabled_transitions(pn, m):
    enabled = set()
    for t in pn.transitions:
        if is_enabled(t, pn, m):
            enabled.add(t)
    return enabled
