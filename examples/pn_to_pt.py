import os
import traceback

import pm4py
from pm4py.evaluation.soundness.woflan import algorithm as woflan
from pm4py.evaluation.wf_net import evaluator as is_wf_net
from pm4py.objects.conversion.process_tree import converter as pt_converter
from pm4py.objects.conversion.wf_net import converter as wf_net_converter


def execute_script():
    log = pm4py.read_xes(os.path.join("..", "tests", "input_data", "running-example.xes"))
    alpha_petri_net, alpha_im, alpha_fm = pm4py.discover_petri_net_alpha(log)
    heuristics_petri_net, heuristics_im, heuristics_fm = pm4py.discover_petri_net_heuristics(log)
    tree = pm4py.discover_tree_inductive(log)
    print("tree discovered by inductive miner=")
    print(tree)
    inductive_petri_net, inductive_im, inductive_fm = pt_converter.apply(tree)
    print("is_wf_net alpha", is_wf_net.apply(alpha_petri_net))
    print("is_wf_net heuristics", is_wf_net.apply(heuristics_petri_net))
    print("is_wf_net inductive", is_wf_net.apply(inductive_petri_net))
    print("woflan alpha", woflan.apply(alpha_petri_net, alpha_im, alpha_fm,
                                       parameters={woflan.Parameters.RETURN_ASAP_WHEN_NOT_SOUND: True,
                                                   woflan.Parameters.PRINT_DIAGNOSTICS: False}))
    print("woflan heuristics", woflan.apply(heuristics_petri_net, heuristics_im, heuristics_fm,
                                            parameters={woflan.Parameters.RETURN_ASAP_WHEN_NOT_SOUND: True,
                                                        woflan.Parameters.PRINT_DIAGNOSTICS: False}))
    print("woflan inductive", woflan.apply(inductive_petri_net, inductive_im, inductive_fm,
                                           parameters={woflan.Parameters.RETURN_ASAP_WHEN_NOT_SOUND: True,
                                                       woflan.Parameters.PRINT_DIAGNOSTICS: False}))
    try:
        tree_alpha = wf_net_converter.apply(alpha_petri_net, alpha_im, alpha_fm)
        print(tree_alpha)
    except:
        traceback.print_exc()
    try:
        tree_heuristics = wf_net_converter.apply(heuristics_petri_net, heuristics_im, heuristics_fm)
        print(tree_heuristics)
    except:
        traceback.print_exc()
    try:
        tree_inductive = wf_net_converter.apply(inductive_petri_net, inductive_im, inductive_fm)
        print(tree_inductive)
        pm4py.view_process_tree(tree_inductive, format="svg")
    except:
        traceback.print_exc()


if __name__ == "__main__":
    execute_script()
