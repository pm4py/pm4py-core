import pm4py
from pm4py.objects.petri_net.obj import ResetInhibitorNet
from pm4py.objects.petri_net.utils import petri_utils
import uuid
import os


def execute_script():
    log = pm4py.read_xes(os.path.join("..", "tests", "input_data", "running-example.xes"))
    net, im, fm = pm4py.discover_petri_net_inductive(log)
    net, im, fm = pm4py.convert_petri_net_type(net, im, fm, type="reset_inhibitor")
    # traditional playout
    new_log = pm4py.play_out(net, im, fm, parameters={"add_only_if_fm_is_reached": True})
    print(len(new_log))
    print(pm4py.get_event_attribute_values(new_log, "concept:name"))
    print(pm4py.get_end_activities(new_log))
    # playout after adding a place with 1 token for every transition
    for trans in net.transitions:
        new_place = ResetInhibitorNet.Place(str(uuid.uuid4()))
        net.places.add(new_place)
        petri_utils.add_arc_from_to(new_place, trans, net, type=None)
        im[new_place] = 1
    pm4py.view_petri_net(net, im, fm, format="svg")
    # ensure that superset of the final marking (given the huge number of remaining tokens) are also considered valid
    new_log2 = pm4py.play_out(net, im, fm, parameters={"add_only_if_fm_is_reached": True, "fm_leq_accepted": True})
    print(len(new_log2))
    print(pm4py.get_event_attribute_values(new_log2, "concept:name"))
    print(pm4py.get_end_activities(new_log2))


if __name__ == "__main__":
    execute_script()
