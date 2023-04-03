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
from pm4py.algo.analysis.woflan.place_invariants.uniform_invariant import apply as compute_uniform_invariants

def apply(net):
    """
    General method to obtain a list of S-components
    :param net: Petri Net for which S-components should be computed
    :return: A list of S-components
    """
    uniform_invariants=compute_uniform_invariants(net)
    return compute_s_components(net, uniform_invariants)


def compute_s_components(net, p_invariants):
    """
    We perform the hint in 5.4.4 of https://pure.tue.nl/ws/portalfiles/portal/1596223/9715985.pdf
    :param p_invariants: Semi-positive basis we calculate previously
    :return: A list of S-Components. A s-component consists of a set which includes all related transitions a places
    """

    def compare_lists(list1, list2):
        """
        :param list1: a list
        :param list2: a list
        :return: a number how often a item from list1 appears in list2
        """
        counter = 0
        for el in list1:
            if el in list2:
                counter += 1
        return counter

    s_components = []
    place_list = sorted(list(net.places), key=lambda x: x.name)
    for invariant in p_invariants:
        i = 0
        s_component = []
        for el in invariant:
            if el > 0:
                place = place_list[i]
                s_component.append(place)
                for in_arc in place.in_arcs:
                    s_component.append(in_arc.source)
                for out_arc in place.out_arcs:
                    s_component.append(out_arc.target)
            i += 1
        if len(s_component) != 0:
            is_s_component = True
            for el in s_component:
                if el in net.transitions:
                    places_before = [arc.source for arc in el.in_arcs]
                    comparison_before = compare_lists(s_component, places_before)
                    places_after = [arc.target for arc in el.out_arcs]
                    comparison_after = compare_lists(s_component, places_after)
                    if comparison_before != 1:
                        is_s_component = False
                        break
                    if comparison_after != 1:
                        is_s_component = False
                        break
            if is_s_component:
                s_components.append(set(s_component))
    return s_components

def compute_uncovered_places_in_component(s_components, net):
    """
    We check for uncovered places
    :param s_components: List of s_components
    :param net: Petri Net representation of PM4Py
    :return: List of uncovered places
    """
    place_list=sorted(list(net.places), key=lambda x: x.name)
    for component in s_components:
        for el in component:
            if el in place_list:
                place_list.remove(el)
    return place_list
