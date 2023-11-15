import pm4py
from pm4py.objects.petri_net.utils import petri_utils
from examples import examples_conf



def execute_script():
    net = pm4py.PetriNet()
    im = pm4py.Marking()
    fm = pm4py.Marking()
    p1 = pm4py.PetriNet.Place("p1")
    p2 = pm4py.PetriNet.Place("p2")
    p3 = pm4py.PetriNet.Place("p3")

    A = pm4py.PetriNet.Transition("A", "A")
    B = pm4py.PetriNet.Transition("B", "B")
    net.places.add(p1)
    net.places.add(p2)
    net.places.add(p3)
    net.transitions.add(A)
    net.transitions.add(B)
    petri_utils.add_arc_from_to(A, p1, net)
    petri_utils.add_arc_from_to(A, p2, net)
    petri_utils.add_arc_from_to(A, p3, net)
    petri_utils.add_arc_from_to(p1, B, net)
    petri_utils.add_arc_from_to(p2, B, net)
    petri_utils.add_arc_from_to(p3, B, net)

    pm4py.view_petri_net(net, im, fm, format=examples_conf.TARGET_IMG_FORMAT)

    net, im, fm = pm4py.reduce_petri_net_implicit_places(net, im, fm)

    pm4py.view_petri_net(net, im, fm, format=examples_conf.TARGET_IMG_FORMAT)


if __name__ == "__main__":
    execute_script()
