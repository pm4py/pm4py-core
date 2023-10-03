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
from collections import Counter
from copy import deepcopy
from typing import Any, Collection, Dict


class Marking(Counter):
    def __hash__(self):
        r = 0
        for p in self.items():
            r += 31 * hash(p[0]) * p[1]
        return r

    def __eq__(self, other):
        if not self.keys() == other.keys():
            return False
        for p in self.keys():
            if other.get(p) != self.get(p):
                return False
        return True

    def __le__(self, other):
        if not self.keys() <= other.keys():
            return False
        for p in self.keys():
            if other.get(p) < self.get(p):
                return False
        return True

    def __add__(self, other):
        m = Marking()
        for p in self.items():
            m[p[0]] = p[1]
        for p in other.items():
            m[p[0]] += p[1]
        return m

    def __sub__(self, other):
        m = Marking()
        for p in self.items():
            m[p[0]] = p[1]
        for p in other.items():
            m[p[0]] -= p[1]
            if m[p[0]] == 0:
                del m[p[0]]
        return m

    def __repr__(self):
        return str([str(p.name) + ":" + str(self.get(p)) for p in sorted(list(self.keys()), key=lambda x: x.name)])

    def __str__(self):
        return self.__repr__()

    def __deepcopy__(self, memodict={}):
        marking = Marking()
        memodict[id(self)] = marking
        for place in self:
            place_occ = self[place]
            new_place = memodict[id(place)] if id(place) in memodict else PetriNet.Place(place.name,
                                                                                         properties=place.properties)
            marking[new_place] = place_occ
        return marking


class PetriNet(object):
    class Place(object):
        __slots__ = ('_name', '_in_arcs', '_out_arcs', '_properties')

        def __init__(self, name, in_arcs=None, out_arcs=None, properties=None):
            self._name = name
            self._in_arcs = set() if in_arcs is None else in_arcs
            self._out_arcs = set() if out_arcs is None else out_arcs
            self._properties = dict() if properties is None else properties

        @property
        def name(self):
            return self._name

        @name.setter
        def name(self, name):
            self._name = name

        @property
        def out_arcs(self):
            return self._out_arcs

        @property
        def in_arcs(self):
            return self._in_arcs

        @property
        def properties(self):
            return self._properties

        def __repr__(self):
            return str(self.name)

        def __str__(self):
            return self.__repr__()

        def __eq__(self, other):
            # keep the ID for now in places
            return id(self) == id(other)

        def __hash__(self):
            # keep the ID for now in places
            return id(self)

        def __deepcopy__(self, memodict={}):
            if id(self) in memodict:
                return memodict[id(self)]
            new_place = PetriNet.Place(self.name, properties=self.properties)
            memodict[id(self)] = new_place
            for arc in self.in_arcs:
                new_arc = deepcopy(arc, memo=memodict)
                new_place.in_arcs.add(new_arc)
            for arc in self.out_arcs:
                new_arc = deepcopy(arc, memo=memodict)
                new_place.out_arcs.add(new_arc)
            return new_place

    class Transition(object):
        __slots__ = ('_name', '_label', '_in_arcs', '_out_arcs', '_properties')

        def __init__(self, name, label=None, in_arcs=None, out_arcs=None, properties=None):
            self._name = name
            self._label = None if label is None else label
            self._in_arcs = set() if in_arcs is None else in_arcs
            self._out_arcs = set() if out_arcs is None else out_arcs
            self._properties = dict() if properties is None else properties

        @property
        def name(self):
            return self._name

        @name.setter
        def name(self, name):
            self._name = name

        @property
        def label(self):
            return self._label

        @label.setter
        def label(self, label):
            self._label = label

        @property
        def out_arcs(self):
            return self._out_arcs

        @property
        def in_arcs(self):
            return self._in_arcs

        @property
        def properties(self):
            return self._properties

        def __repr__(self):
            if self.label is None:
                return "("+str(self.name)+", None)"
            else:
                return "("+str(self.name)+", '"+str(self.label)+"')"

        def __str__(self):
            return self.__repr__()

        def __eq__(self, other):
            # keep the ID for now in transitions
            return id(self) == id(other)

        def __hash__(self):
            # keep the ID for now in transitions
            return id(self)

        def __deepcopy__(self, memodict={}):
            if id(self) in memodict:
                return memodict[id(self)]
            new_trans = PetriNet.Transition(self.name, self.label, properties=self.properties)
            memodict[id(self)] = new_trans
            for arc in self.in_arcs:
                new_arc = deepcopy(arc, memo=memodict)
                new_trans.in_arcs.add(new_arc)
            for arc in self.out_arcs:
                new_arc = deepcopy(arc, memo=memodict)
                new_trans.out_arcs.add(new_arc)
            return new_trans

    class Arc(object):
        __slots__ = ('_source', '_target', '_weight', '_properties')

        def __init__(self, source, target, weight=1, properties=None):
            if type(source) is type(target):
                raise Exception('Petri nets are bipartite graphs!')
            self._source = source
            self._target = target
            self._weight = weight
            self._properties = dict() if properties is None else properties

        @property
        def source(self):
            return self._source

        @property
        def target(self):
            return self._target

        @property
        def weight(self):
            return self._weight

        @weight.setter
        def weight(self, weight):
            self._weight = weight

        @property
        def properties(self):
            return self._properties

        def __repr__(self):
            source_rep = repr(self.source)
            target_rep = repr(self.target)
            return source_rep+"->"+target_rep

        def __str__(self):
            return self.__repr__()

        def __hash__(self):
            return id(self)

        def __eq__(self, other):
            return self.source == other.source and self.target == other.target

        def __deepcopy__(self, memodict={}):
            if id(self) in memodict:
                return memodict[id(self)]
            new_source = memodict[id(self.source)] if id(self.source) in memodict else deepcopy(self.source,
                                                                                                memo=memodict)
            new_target = memodict[id(self.target)] if id(self.target) in memodict else deepcopy(self.target,
                                                                                                memo=memodict)
            memodict[id(self.source)] = new_source
            memodict[id(self.target)] = new_target
            new_arc = PetriNet.Arc(new_source, new_target, weight=self.weight, properties=self.properties)
            memodict[id(self)] = new_arc
            return new_arc

    def __init__(self, name: str=None, places: Collection[Place]=None, transitions: Collection[Transition]=None, arcs: Collection[Arc]=None, properties:Dict[str, Any]=None):
        self._name = "" if name is None else name
        self._places = set() if places is None else places
        self._transitions = set() if transitions is None else transitions
        self._arcs = set() if arcs is None else arcs
        self._properties = dict() if properties is None else properties

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, name):
        self._name = name

    @property
    def places(self) -> Collection[Place]:
        return self._places

    @property
    def transitions(self) -> Collection[Transition]:
        return self._transitions

    @property
    def arcs(self) -> Collection[Arc]:
        return self._arcs

    @property
    def properties(self) -> Dict[str, Any]:
        return self._properties

    def __hash__(self):
        ret = 0
        for p in self.places:
            ret += hash(p)
            ret = ret % 479001599
        for t in self.transitions:
            ret += hash(t)
            ret = ret % 479001599
        return ret

    def __eq__(self, other):
        # for the Petri net equality keep the ID for now
        return id(self) == id(other)

    def __deepcopy__(self, memodict={}):
        from pm4py.objects.petri_net.utils.petri_utils import add_arc_from_to
        this_copy = PetriNet(self.name)
        memodict[id(self)] = this_copy
        for place in self.places:
            place_copy = PetriNet.Place(place.name, properties=place.properties)
            this_copy.places.add(place_copy)
            memodict[id(place)] = place_copy
        for trans in self.transitions:
            trans_copy = PetriNet.Transition(trans.name, trans.label, properties=trans.properties)
            this_copy.transitions.add(trans_copy)
            memodict[id(trans)] = trans_copy
        for arc in self.arcs:
            add_arc_from_to(memodict[id(arc.source)], memodict[id(arc.target)], this_copy, weight=arc.weight)
        return this_copy

    def __repr__(self):
        ret = ["places: ["]
        places_rep = []
        for place in self.places:
            places_rep.append(repr(place))
        places_rep.sort()
        ret.append(" " + ", ".join(places_rep) + " ")
        ret.append("]\ntransitions: [")
        trans_rep = []
        for trans in self.transitions:
            trans_rep.append(repr(trans))
        trans_rep.sort()
        ret.append(" " + ", ".join(trans_rep) + " ")
        ret.append("]\narcs: [")
        arcs_rep = []
        for arc in self.arcs:
            arcs_rep.append(repr(arc))
        arcs_rep.sort()
        ret.append(" " + ", ".join(arcs_rep) + " ")
        ret.append("]")
        return "".join(ret)

    def __str__(self):
        return self.__repr__()


class InhibitorNet(PetriNet):
    def __init__(self, name=None, places=None, transitions=None, arcs=None, properties=None):
        PetriNet.__init__(self, name=name, places=places, transitions=transitions, arcs=arcs, properties=properties)

    class InhibitorArc(PetriNet.Arc):
        def __init__(self, source, target, weight=1, properties=None):
            PetriNet.Arc.__init__(self, source, target, weight=weight, properties=properties)


class ResetNet(PetriNet):
    def __init__(self, name=None, places=None, transitions=None, arcs=None, properties=None):
        PetriNet.__init__(self, name=name, places=places, transitions=transitions, arcs=arcs, properties=properties)

    class ResetArc(PetriNet.Arc):
        def __init__(self, source, target, weight=1, properties=None):
            PetriNet.Arc.__init__(self, source, target, weight=weight, properties=properties)


class ResetInhibitorNet(InhibitorNet, ResetNet):
    def __init__(self, name=None, places=None, transitions=None, arcs=None, properties=None):
        PetriNet.__init__(self, name=name, places=places, transitions=transitions, arcs=arcs, properties=properties)
