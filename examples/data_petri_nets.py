import os

import pm4py
from pm4py.algo.conformance.alignments.petri_net import algorithm as alignments
from pm4py.objects.petri_net.data_petri_nets import semantics
from pm4py.objects.petri_net.data_petri_nets.data_marking import DataMarking


def get_trans_by_name(net, name):
    ret = [x for x in net.transitions if x.name == name]
    if len(ret) == 0:
        return None
    return ret[0]


def execute_script():
    log = pm4py.read_xes(os.path.join("..", "tests", "input_data", "roadtraffic100traces.xes"))
    net, im, fm = pm4py.read_pnml(os.path.join("..", "tests", "input_data", "data_petri_net.pnml"), auto_guess_final_marking=True)
    pm4py.view_petri_net(net, im, fm, format="svg")
    aligned_traces = alignments.apply(log, net, im, fm, variant=alignments.Variants.VERSION_DIJKSTRA_LESS_MEMORY, parameters={"ret_tuple_as_trans_desc": True})
    for index, trace in enumerate(log):
        aligned_trace = aligned_traces[index]
        al = [(x[0][0], get_trans_by_name(net, x[0][1])) for x in aligned_trace["alignment"]]
        m = DataMarking(im)
        idx = 0
        for el in al:
            if el[1] is not None:
                en_t = semantics.enabled_transitions(net, m, trace[min(idx, len(trace) - 1)])
                if el[1] in en_t:
                    if "guard" in el[1].properties:
                        print(el[1], "GUARD SATISFIED", el[1].properties["guard"], m)
                    m = semantics.execute(el[1], net, m, trace[min(idx, len(trace) - 1)])
                else:
                    print("TRANSITION UNAVAILABLE! Guards are blocking")
            if el[0] != ">>":
                idx = idx + 1


if __name__ == "__main__":
    execute_script()
