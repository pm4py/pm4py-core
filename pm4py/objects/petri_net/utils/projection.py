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
import numpy as np

from pm4py.objects.petri_net.obj import PetriNet, Marking
from pm4py.objects.petri_net.utils.petri_utils import add_arc_from_to


def project_net_on_place(place):
    """
    Project a Petri net on a place

    Parameters
    -------------
    place
        Place

    Returns
    -------------
    net
        (Place) net
    im
        Empty initial marking
    fm
        Empty final marking
    """
    place_net = PetriNet()
    place_net_im = Marking()
    place_net_fm = Marking()

    input_trans = [arc.source for arc in place.in_arcs]
    output_trans = [arc.target for arc in place.out_arcs]

    if len(input_trans) == 0 or len(output_trans) == 0:
        raise Exception("place projection not available on source/sink places")

    input_trans_visible = [trans for trans in input_trans if trans.label]
    output_trans_visible = [trans for trans in output_trans if trans.label]

    if not len(input_trans) == len(input_trans_visible) or not len(output_trans) == len(output_trans_visible):
        raise Exception("place projection not available on places that have invisible transitions as preset/postset")

    new_place = PetriNet.Place(place.name)
    place_net.places.add(new_place)

    for trans in input_trans:
        new_trans = PetriNet.Transition(trans.name, trans.label)
        place_net.transitions.add(new_trans)
        add_arc_from_to(new_trans, new_place, place_net)

    for trans in output_trans:
        new_trans = PetriNet.Transition(trans.name, trans.label)
        place_net.transitions.add(new_trans)
        add_arc_from_to(new_place, new_trans, place_net)

    return place_net, place_net_im, place_net_fm


def project_net_on_matrix(net, activities, parameters=None):
    """
    Project a Petri net with:
    - only visible transitions
    - where each place preset/postset is disjoint
    - with unique visible transitions
    on a numeric matrix

    Parameters
    --------------
    net
        Petri net
    activities
        List of activities
    parameters
        Possible parameters of the algorithm
    """
    inv_trans_map = {}
    for trans in net.transitions:
        if not trans.label:
            raise Exception(
                "the project_net_on_matrix works only with Petri net that do not contain invisible transitions")
        if trans.label in inv_trans_map:
            raise Exception(
                "the project_net_on_matrix works only with Petri net that contains unique visible transitions")
        inv_trans_map[trans.label] = trans
    places_matrix = []
    for place in net.places:
        place_repr = [0] * len(activities)
        input_trans_labels = set([arc.source.label for arc in place.in_arcs])
        output_trans_labels = set([arc.target.label for arc in place.out_arcs])
        if len(input_trans_labels.intersection(output_trans_labels)) > 0:
            raise Exception("place has a transition that belongs to both preset and postset")
        for arc in place.in_arcs:
            input_trans_label = arc.source.label
            input_arc_weight = arc.weight
            if input_trans_label in activities:
                place_repr[activities.index(input_trans_label)] = -input_arc_weight
        for arc in place.out_arcs:
            output_trans_label = arc.target.label
            output_arc_weight = arc.weight
            if output_trans_label in activities:
                place_repr[activities.index(output_trans_label)] = output_arc_weight
        if min(place_repr) < 0 < max(place_repr):
            places_matrix.append(place_repr)
    if len(places_matrix) == 0:
        raise Exception("no places numeric representation could be found")
    places_matrix = np.transpose(np.asmatrix(places_matrix))
    return places_matrix
