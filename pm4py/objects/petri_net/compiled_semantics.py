from typing import TypeVar
from collections import Counter
from itertools import chain
from pm4py.objects.petri_net.obj import PetriNet, Marking
from pm4py.objects.petri_net.sem_interface import Semantics

N = TypeVar("N", bound=PetriNet)
T = TypeVar("T", bound=PetriNet.Transition)
P = TypeVar("P", bound=PetriNet.Place)


class CompiledClassicSemantics(Semantics):
    """
    This class implements the "compiled" Petri nets semantics.
    Basically, it pre-processes the Petri net to compute pre-/post-sets of its transitions
        as well as the delta of each transition firing.
    This makes the four interface operations much faster.
    The downside is that the Petri net cannot be changed,
        this is checked and in case of failure an error is thrown.
    """
    __slots__ = (
        '_pn', '_transition_pre_sets', '_transition_deltas',
        '_no_pre_conditions', '_place_post_sets'
    )

    def __init__(self, pn: PetriNet):
        self._pn = pn
        self._transition_pre_sets = {
            t: list(_get_transition_pre_set(t).items()) for t in pn.transitions
        }
        self._transition_deltas = {t: _get_transition_delta(t) for t in pn.transitions}
        self._no_pre_conditions = {
            t for t in pn.transitions if _transition_has_no_pre_condition(t)
        }
        self._place_post_sets = {p: _get_place_post_set(p) for p in pn.places}

    def _check_is_same_net(self, other_net):
        # This is to keep compatibility with the existing semantics API,
        #   but ideally the interface should not allow a Petri net as a parameter
        if self._pn != other_net:
            raise ValueError("Input Petri nets for compiled semantics are not the same")

    def _is_enabled(self, t, m, **kwargs):
        # Check if transition is enabled
        place_counts = self._transition_pre_sets[t]

        for place, count in place_counts:
            if m[place] < count:
                return False
        return True

    def is_enabled(self, t, pn, m, **kwargs):
        self._check_is_same_net(pn)
        return self._is_enabled(t, m, **kwargs)

    def _do_execute(self, t, m, **kwargs):
        if not self._is_enabled(t, m):
            return None

        return self._do_weak_execute(t, m)

    def execute(self, t, pn, m, **kwargs):
        self._check_is_same_net(pn)
        return self._do_execute(t, m, **kwargs)

    def _do_weak_execute(self, t, m, **kwargs):
        m_out = Marking(m.copy())
        for place, count in self._transition_deltas[t]:
            m_out[place] += count
            if count < 0 and m_out[place] == 0:
                del m_out[place]

        return m_out

    def weak_execute(self, t, pn, m, **kwargs):
        self._check_is_same_net(pn)
        return self._do_weak_execute(t, m, **kwargs)

    def _enabled_transitions(self, m, **kwargs):
        transitions_to_fire = {*chain.from_iterable(self._place_post_sets[p] for p in m)}
        return self._no_pre_conditions.union(t for t in transitions_to_fire if self._is_enabled(t, m))

    def enabled_transitions(self, pn, m, **kwargs):
        self._check_is_same_net(pn)
        return self._enabled_transitions(m, **kwargs)


def _get_transition_pre_set(transition: PetriNet.Transition):
    return Counter({in_arc.source: in_arc.weight for in_arc in transition.in_arcs})


def _get_transition_post_set(transition: PetriNet.Transition):
    return Counter({out_arc.target: out_arc.weight for out_arc in transition.out_arcs})


def _get_transition_delta(transition: PetriNet.Transition):
    # The delta is supposed to be ADDED to the current marking to get the subsequent marking
    pre_set = _get_transition_pre_set(transition)
    post_set = _get_transition_post_set(transition)
    post_set.subtract(pre_set)
    return list(post_set.items())


def _transition_has_no_pre_condition(transition: PetriNet.Transition):
    return all(arc.weight == 0 for arc in transition.in_arcs)


def _get_place_post_set(place: PetriNet.Place):
    return [out_arc.target for out_arc in place.out_arcs]
