from pm4py.algo.discovery.dfg.utils import dfg_utils
from pm4py.objects.petri.petrinet import PetriNet, Marking
from pm4py.objects.petri.utils import add_arc_from_to

PARAM_KEY_START_ACTIVITIES = 'start_activities'
PARAM_KEY_END_ACTIVITIES = 'end_activities'


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
    start_activities = parameters[PARAM_KEY_START_ACTIVITIES] if PARAM_KEY_START_ACTIVITIES in parameters else dfg_utils.infer_start_activities(dfg)
    end_activities = parameters[PARAM_KEY_END_ACTIVITIES] if PARAM_KEY_END_ACTIVITIES in parameters else dfg_utils.infer_end_activities(dfg)
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
            add_arc_from_to(source, trans, net)
            add_arc_from_to(trans, places_corr[act], net)

    for act in end_activities:
        if act in places_corr:
            index = index + 1
            inv_trans = PetriNet.Transition(act + "_" + str(index), None)
            net.transitions.add(inv_trans)
            add_arc_from_to(places_corr[act], inv_trans, net)
            add_arc_from_to(inv_trans, sink, net)

    for el in dfg.keys():
        act1 = el[0]
        act2 = el[1]

        index = index + 1
        trans = PetriNet.Transition(act2 + "_" + str(index), act2)
        net.transitions.add(trans)

        add_arc_from_to(places_corr[act1], trans, net)
        add_arc_from_to(trans, places_corr[act2], net)

    return net, im, fm
