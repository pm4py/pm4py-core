import pm4py
from pm4py.objects.petri_net.obj import ResetInhibitorNet, Marking
from pm4py.objects.petri_net.utils.petri_utils import add_arc_from_to
from pm4py.objects.petri_net.inhibitor_reset import semantics
from copy import deepcopy


def execute_script():
    net = ResetInhibitorNet("")
    source = ResetInhibitorNet.Place("source")
    sink = ResetInhibitorNet.Place("sink")
    p1 = ResetInhibitorNet.Place("p1")
    p2 = ResetInhibitorNet.Place("p2")
    p_inhibitor = ResetInhibitorNet.Place("p_inhibitor")
    p_reset = ResetInhibitorNet.Place("p_reset")
    trans_A = ResetInhibitorNet.Transition("A", "A")
    trans_B = ResetInhibitorNet.Transition("B", "B")
    trans_C = ResetInhibitorNet.Transition("C", "C")
    trans_inhibitor = ResetInhibitorNet.Transition("inhibitor", None)
    trans_free = ResetInhibitorNet.Transition("free", None)
    net.places.add(source)
    net.places.add(sink)
    net.places.add(p1)
    net.places.add(p2)
    net.places.add(p_inhibitor)
    net.places.add(p_reset)
    net.transitions.add(trans_A)
    net.transitions.add(trans_B)
    net.transitions.add(trans_C)
    net.transitions.add(trans_free)
    net.transitions.add(trans_inhibitor)
    add_arc_from_to(source, trans_A, net)
    add_arc_from_to(trans_A, p1, net)
    add_arc_from_to(p1, trans_B, net)
    add_arc_from_to(trans_B, p2, net)
    add_arc_from_to(p2, trans_C, net)
    add_arc_from_to(trans_C, sink, net)
    add_arc_from_to(trans_inhibitor, p_inhibitor, net)
    inhibitor_arc = add_arc_from_to(p_inhibitor, trans_B, net, type="inhibitor")
    add_arc_from_to(trans_free, p_reset, net)
    reset_arc = add_arc_from_to(p_reset, trans_C, net, type="reset")
    im = Marking({source: 1})
    fm = Marking({sink: 1})
    pm4py.view_petri_net(net, im, fm, format="svg")
    m = semantics.execute(trans_A, net, im)
    print(m)
    # B is enabled in m because no tokens in the "inhibitor" place
    print(semantics.enabled_transitions(net, m))
    # if we put a token in the inhibitor place, B is not enabled anymore
    m2 = deepcopy(m)
    m2[p_inhibitor] = 1
    print(semantics.enabled_transitions(net, m2))
    # let's continue with m and fire B, and three times the "free" transition
    m = semantics.execute(trans_B, net, m)
    m = semantics.execute(trans_free, net, m)
    m = semantics.execute(trans_free, net, m)
    m = semantics.execute(trans_free, net, m)
    # we have three tokens in the 'reset' place. Firing C, all of them are removed because of the reset arc
    print(m)
    m = semantics.execute(trans_C, net, m)
    print(m)
    print(m == fm)
    # sink reached :)


if __name__ == "__main__":
    execute_script()
