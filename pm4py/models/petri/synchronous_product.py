from pm4py.models import petri
from pm4py.log.util import xes as xes_util
import time


def construct(pn, marking, trace, skip, activity_key=xes_util.DEFAULT_NAME_KEY):
    '''
    Constructs the synchronous product net of a petri net and a trace.
    It assumes the input Petri net to be a Workflow net (i.e. all elements connected)

    Parameters
    ----------
    :param pn:
    :param marking:
    :param trace:
    :param activity_key: key of event that relates to the activity name of the event

    Returns
    -------
    :return: Synchronous product net and associated marking labels are of the form (a,>>)
    '''
    sync_net, sync_marking = __construct_trace_net(trace, skip, petri.instance.PetriNet('synchronous_product_net_of_'+pn.name+'_and_a_trace'))
    tr_map = {}
    pl_map = {}
    for t in pn.transitions:
        # cloning model part
        t_clone = petri.instance.PetriNet.Transition('sn_m_t_'+str(t.name), (skip, t.label))
        sync_net.transitions.add(t_clone)
        tr_map[t] = t_clone
        for a in t.in_arcs:
            if a.source not in pl_map:
                pl_map[a.source] = petri.instance.PetriNet.Place('sn_m_p_'+str(a.source.name))
                sync_net.places.add(pl_map[a.source])
            petri.utils.add_arc_from_to(pl_map[a.source], tr_map[t], sync_net)
        for a in t.out_arcs:
            if a.target not in pl_map:
                pl_map[a.target] = petri.instance.PetriNet.Place('sn_m_p_'+str(a.target.name))
                sync_net.places.add(pl_map[a.target])
            petri.utils.add_arc_from_to(tr_map[t], pl_map[a.target], sync_net)

        # adding synchronous part
        for e in trace:
            if e[activity_key] is t.label:
                for t_log in sync_net.transitions.copy():
                    if t_log.label[1] is skip and t_log.label[0][activity_key] is t.label:
                        sync_tr = petri.instance.PetriNet.Transition('sn_sync_'+t.name+t_log.name, (t_log.label[0], t.name))
                        sync_net.transitions.add(sync_tr)
                        for a in t_log.in_arcs:
                            petri.utils.add_arc_from_to(a.source, sync_tr, sync_net)
                        for a in t_log.out_arcs:
                            petri.utils.add_arc_from_to(sync_tr, a.target, sync_net)
                        for a in tr_map[t].in_arcs:
                            petri.utils.add_arc_from_to(a.source, sync_tr, sync_net)
                        for a in tr_map[t].out_arcs:
                            petri.utils.add_arc_from_to(sync_tr, a.target, sync_net)
    for p in marking:
        sync_marking[pl_map[p]] += marking[p]
    return sync_net, sync_marking


def __construct_trace_net(trace, skip, tn):
    source = petri.instance.PetriNet.Place('sn_tn_source')
    sink = petri.instance.PetriNet.Place('sn_tn_sink')
    place_map = {}
    for i in range(0, len(trace) - 1):
        t = petri.instance.PetriNet.Transition('sn_tn_t_'+str(i), (trace[i], skip))
        tn.transitions.add(t)
        place_map[i] = petri.instance.PetriNet.Place('sn_tn_p_'+str(i))
        tn.places.add(place_map[i])
        petri.utils.add_arc_from_to(source, t, tn) if i == 0 else petri.utils.add_arc_from_to(place_map[i - 1], t, tn)
        petri.utils.add_arc_from_to(t, place_map[i], tn) if i < len(trace) - 1 else petri.utils.add_arc_from_to(t, sink, tn)
    return tn, petri.instance.Marking({source: 1})

