import os
import traceback

import pm4py
from pm4py.algo.discovery.inductive import algorithm as inductive
from pm4py.objects.log.importer.xes import importer as xes_importer
from pm4py.visualization.petri_net import visualizer as pn_vis
from pm4py.objects.conversion.process_tree import converter as process_tree_converter


def execute_script():
    log_path = os.path.join("..", "tests", "input_data", "running-example.xes")

    log = xes_importer.apply(log_path)
    process_tree = inductive.apply(log)
    net, marking, final_marking = process_tree_converter.apply(process_tree)
    for place in marking:
        print("initial marking " + place.name)
    for place in final_marking:
        print("final marking " + place.name)
    gviz = pn_vis.apply(net, marking, final_marking,
                        parameters={pn_vis.Variants.WO_DECORATION.value.Parameters.FORMAT: "svg",
                                    pn_vis.Variants.WO_DECORATION.value.Parameters.DEBUG: True})
    pn_vis.view(gviz)

    if True:
        fit_traces = []

        for i in range(0, len(log)):
            try:
                print("\n", i, [x["concept:name"] for x in log[i]])
                cf_result = pm4py.algo.conformance.alignments.petri_net.variants.state_equation_a_star.apply(log[i], net, marking,
                                                                                                   final_marking)[
                    'alignment']
                if cf_result is None:
                    print("alignment is none!")
                else:
                    is_fit = True
                    for couple in cf_result:
                        print(couple)
                        if not (couple[0] == couple[1] or couple[0] == ">>" and couple[1] is None):
                            is_fit = False
                    print("isFit = " + str(is_fit))

                    if is_fit:
                        fit_traces.append(log[i])
            except TypeError:
                print("EXCEPTION ", i)
                traceback.print_exc()
        print(fit_traces)
        print(len(fit_traces))


if __name__ == "__main__":
    execute_script()
