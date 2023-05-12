from pm4py.objects.petri_net.obj import Marking
from pm4py.objects.petri_net.utils import petri_utils
from pm4py.objects.petri_net.saw_net.obj import StochasticArcWeightNet
from uuid import uuid4
from pm4py.visualization.petri_net import visualizer as pn_visualizer
import os


def execute_script():
    neto = StochasticArcWeightNet()
    imo = Marking()
    fmo = Marking()
    sourceo = StochasticArcWeightNet.Place("sourceo")
    targeto = StochasticArcWeightNet.Place("targeto")
    # imo[sourceo] = 1
    # fmo[targeto] = 1
    neto.places.add(sourceo)
    neto.places.add(targeto)
    create_order_o = StochasticArcWeightNet.Transition(str(uuid4()), "Create Order")
    send_package_o = StochasticArcWeightNet.Transition(str(uuid4()), "Send Package")
    pay_order_o = StochasticArcWeightNet.Transition(str(uuid4()), "Pay Order")
    item_issue_o = StochasticArcWeightNet.Transition(str(uuid4()), "Item Issue")
    item_fixed_o = StochasticArcWeightNet.Transition(str(uuid4()), "Item Fixed")
    skip_o = StochasticArcWeightNet.Transition(str(uuid4()), None)
    neto.transitions.add(create_order_o)
    neto.transitions.add(send_package_o)
    neto.transitions.add(pay_order_o)
    neto.transitions.add(item_issue_o)
    neto.transitions.add(item_fixed_o)
    neto.transitions.add(skip_o)
    p1o = StochasticArcWeightNet.Place("p1o")
    p2o = StochasticArcWeightNet.Place("p2o")
    p3o = StochasticArcWeightNet.Place("p3o")
    p4o = StochasticArcWeightNet.Place("p4o")
    neto.places.add(p1o)
    neto.places.add(p2o)
    neto.places.add(p3o)
    neto.places.add(p4o)
    arc1o = petri_utils.add_arc_from_to(sourceo, create_order_o, neto, type="stochastic_arc")
    arc2o = petri_utils.add_arc_from_to(create_order_o, p1o, neto, type="stochastic_arc")
    arc3o = petri_utils.add_arc_from_to(p1o, item_issue_o, neto, type="stochastic_arc")
    arc4o = petri_utils.add_arc_from_to(p1o, skip_o, neto, type="stochastic_arc")
    arc5o = petri_utils.add_arc_from_to(item_issue_o, p2o, neto, type="stochastic_arc")
    arc6o = petri_utils.add_arc_from_to(p2o, item_fixed_o, neto, type="stochastic_arc")
    arc7o = petri_utils.add_arc_from_to(item_fixed_o, p3o, neto, type="stochastic_arc")
    arc8o = petri_utils.add_arc_from_to(p3o, send_package_o, neto, type="stochastic_arc")
    arc9o = petri_utils.add_arc_from_to(skip_o, p3o, neto, type="stochastic_arc")
    arc10o = petri_utils.add_arc_from_to(send_package_o, p4o, neto, type="stochastic_arc")
    arc11o = petri_utils.add_arc_from_to(p4o, pay_order_o, neto, type="stochastic_arc")
    arc12o = petri_utils.add_arc_from_to(pay_order_o, targeto, neto, type="stochastic_arc")
    arc1o.weight = {1: 3}
    arc2o.weight = {1: 3}
    arc3o.weight = {1: 1}
    arc4o.weight = {1: 2}
    arc5o.weight = {1: 1}
    arc6o.weight = {1: 1}
    arc7o.weight = {1: 1}
    arc8o.weight = {1: 3}
    arc9o.weight = {1: 2}
    arc10o.weight = {1: 3}
    arc11o.weight = {1: 3}
    arc12o.weight = {1: 3}

    gviz = pn_visualizer.apply(neto, imo, fmo)
    pn_visualizer.save(gviz, "folded_order.png")

    nete = StochasticArcWeightNet()
    ime = Marking()
    fme = Marking()
    sourcee = StochasticArcWeightNet.Place("source")
    targete = StochasticArcWeightNet.Place("targete")
    nete.places.add(sourcee)
    nete.places.add(targete)
    # ime[sourcee] = 3
    # fme[targete] = 3
    create_order_e = StochasticArcWeightNet.Transition(str(uuid4()), "Create Order")
    send_package_e = StochasticArcWeightNet.Transition(str(uuid4()), "Send Package")
    item_issue_e = StochasticArcWeightNet.Transition(str(uuid4()), "Item Issue")
    item_fixed_e = StochasticArcWeightNet.Transition(str(uuid4()), "Item Fixed")
    skip_e = StochasticArcWeightNet.Transition(str(uuid4()), None)
    nete.transitions.add(create_order_e)
    nete.transitions.add(send_package_e)
    nete.transitions.add(item_issue_e)
    nete.transitions.add(item_fixed_e)
    nete.transitions.add(skip_e)
    p1e = StochasticArcWeightNet.Place("p1e")
    p2e = StochasticArcWeightNet.Place("p2e")
    p3e = StochasticArcWeightNet.Place("p3e")
    nete.places.add(p1e)
    nete.places.add(p2e)
    nete.places.add(p3e)
    arc1 = petri_utils.add_arc_from_to(sourcee, create_order_e, nete, type="stochastic_arc")
    arc2 = petri_utils.add_arc_from_to(create_order_e, p1e, nete, type="stochastic_arc")
    arc3 = petri_utils.add_arc_from_to(p1e, skip_e, nete, type="stochastic_arc")
    arc4 = petri_utils.add_arc_from_to(p1e, item_issue_e, nete, type="stochastic_arc")
    arc5 = petri_utils.add_arc_from_to(item_issue_e, p2e, nete, type="stochastic_arc")
    arc6 = petri_utils.add_arc_from_to(p2e, item_fixed_e, nete, type="stochastic_arc")
    arc7 = petri_utils.add_arc_from_to(item_fixed_e, p3e, nete, type="stochastic_arc")
    arc8 = petri_utils.add_arc_from_to(skip_e, p3e, nete, type="stochastic_arc")
    arc9 = petri_utils.add_arc_from_to(p3e, send_package_e, nete, type="stochastic_arc")
    arc10 = petri_utils.add_arc_from_to(send_package_e, targete, nete, type="stochastic_arc")
    arc1.weight = {2: 1, 3: 2}
    arc2.weight = {2: 1, 3: 2}
    arc3.weight = {2: 2, 3: 1}
    arc4.weight = {1: 1}
    arc5.weight = {1: 1}
    arc6.weight = {1: 1}
    arc7.weight = {1: 1}
    arc8.weight = {2: 2, 3: 1}
    arc9.weight = {2: 1, 3: 2}
    arc10.weight = {2: 1, 3: 2}

    gviz = pn_visualizer.apply(nete, ime, fme)
    pn_visualizer.save(gviz, "folded_item.png")

    os.remove("folded_order.png")
    os.remove("folded_item.png")


if __name__ == "__main__":
    execute_script()
