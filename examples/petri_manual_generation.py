import pm4py
from pm4py.objects.petri_net.obj import PetriNet, Marking
from pm4py.objects.petri_net.utils import petri_utils


def execute_script():
    net = PetriNet("test")
    source = PetriNet.Place("source")
    sink = PetriNet.Place("sink")
    p1 = PetriNet.Place("p1")
    p2 = PetriNet.Place("p2")
    p3 = PetriNet.Place("p3")
    p4 = PetriNet.Place("p4")
    t1 = PetriNet.Transition("Confirmation of receipt", "Confirmation of receipt")
    t2 = PetriNet.Transition("T02 Check confirmation of receipt", "T02 Check confirmation of receipt")
    t3 = PetriNet.Transition("T04 Determine confirmation of receipt", "T04 Determine confirmation of receipt")
    t4 = PetriNet.Transition("T05 Print and send confirmation of receipt", "T05 Print and send confirmation of receipt")
    t5 = PetriNet.Transition("T06 Determine necessity of stop advice", "T06 Determine necessity of stop advice")

    net.places.add(source)
    net.places.add(sink)
    net.places.add(p1)
    net.places.add(p2)
    net.places.add(p3)
    net.places.add(p4)
    net.transitions.add(t1)
    net.transitions.add(t2)
    net.transitions.add(t3)
    net.transitions.add(t4)
    net.transitions.add(t5)

    petri_utils.add_arc_from_to(source, t1, net)
    petri_utils.add_arc_from_to(t1, p1, net)
    petri_utils.add_arc_from_to(p1, t2, net)
    petri_utils.add_arc_from_to(t2, p2, net)
    petri_utils.add_arc_from_to(p2, t3, net)
    petri_utils.add_arc_from_to(t3, p3, net)
    petri_utils.add_arc_from_to(p3, t4, net)
    petri_utils.add_arc_from_to(t4, p4, net)
    petri_utils.add_arc_from_to(p4, t5, net)
    petri_utils.add_arc_from_to(t5, sink, net)

    im = Marking()
    im[source] = 1

    fm = Marking()
    fm[sink] = 1

    pm4py.view_petri_net(net, im, fm, format="svg")

    #pm4py.write_pnml(net, im, fm, "receipt_one_variant.pnml")


if __name__ == "__main__":
    execute_script()
