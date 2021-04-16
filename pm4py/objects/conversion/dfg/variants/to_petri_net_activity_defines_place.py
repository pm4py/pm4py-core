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
from pm4py.objects.dfg.utils import dfg_utils
from pm4py.objects.petri_net.obj import PetriNet, Marking
from pm4py.objects.petri_net.utils import petri_utils as pn_util
from enum import Enum
from pm4py.util import exec_utils


class Parameters(Enum):
    START_ACTIVITIES = 'start_activities'
    END_ACTIVITIES = 'end_activities'


PARAM_KEY_START_ACTIVITIES = Parameters.START_ACTIVITIES
PARAM_KEY_END_ACTIVITIES = Parameters.END_ACTIVITIES


def apply(dfg, parameters=None):
    """
    Applies the DFG mining on a given object (if it is a Pandas dataframe or a log, the DFG is calculated)

    Parameters
    -------------
    dfg
        Object (DFG) (if it is a Pandas dataframe or a log, the DFG is calculated)
    parameters
        Parameters
    """
    if parameters is None:
        parameters = {}

    dfg = dfg
    start_activities = exec_utils.get_param_value(Parameters.START_ACTIVITIES, parameters,
                                                  dfg_utils.infer_start_activities(
                                                      dfg))
    end_activities = exec_utils.get_param_value(Parameters.END_ACTIVITIES, parameters,
                                                dfg_utils.infer_end_activities(dfg))
    activities = dfg_utils.get_activities_from_dfg(dfg)

    net = PetriNet("")
    im = Marking()
    fm = Marking()

    source = PetriNet.Place("source")
    net.places.add(source)
    im[source] = 1
    sink = PetriNet.Place("sink")
    net.places.add(sink)
    fm[sink] = 1

    places_corr = {}
    index = 0

    for act in activities:
        places_corr[act] = PetriNet.Place(act)
        net.places.add(places_corr[act])

    for act in start_activities:
        if act in places_corr:
            index = index + 1
            trans = PetriNet.Transition(act + "_" + str(index), act)
            net.transitions.add(trans)
            pn_util.add_arc_from_to(source, trans, net)
            pn_util.add_arc_from_to(trans, places_corr[act], net)

    for act in end_activities:
        if act in places_corr:
            index = index + 1
            inv_trans = PetriNet.Transition(act + "_" + str(index), None)
            net.transitions.add(inv_trans)
            pn_util.add_arc_from_to(places_corr[act], inv_trans, net)
            pn_util.add_arc_from_to(inv_trans, sink, net)

    for el in dfg.keys():
        act1 = el[0]
        act2 = el[1]

        index = index + 1
        trans = PetriNet.Transition(act2 + "_" + str(index), act2)
        net.transitions.add(trans)

        pn_util.add_arc_from_to(places_corr[act1], trans, net)
        pn_util.add_arc_from_to(trans, places_corr[act2], net)

    return net, im, fm
