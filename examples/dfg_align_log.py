import os
import time

import pm4py
from pm4py.algo.conformance.alignments import algorithm as petri_alignments
from pm4py.objects.dfg.filtering import dfg_filtering
from pm4py.objects.dfg.utils import dfg_alignment
from pm4py.statistics.attributes.log import get
from pm4py.visualization.dfg import visualizer


def execute_script():
    log = pm4py.read_xes(os.path.join("..", "tests", "input_data", "receipt.xes"))
    print("number of cases", len(log))
    print("number of events", sum(len(x) for x in log))
    print("number of variants", len(pm4py.get_variants(log)))
    ac = get.get_attribute_values(log, "concept:name")
    dfg, sa, ea = pm4py.discover_dfg(log)
    perc = 0.5
    dfg, sa, ea, ac = dfg_filtering.filter_dfg_on_activities_percentage(dfg, sa, ea, ac, perc)
    dfg, sa, ea, ac = dfg_filtering.filter_dfg_on_paths_percentage(dfg, sa, ea, ac, perc)
    aa = time.time()
    aligned_traces = dfg_alignment.apply(log, dfg, sa, ea)
    bb = time.time()
    net, im, fm = pm4py.convert_to_petri_net(dfg, sa, ea)
    for trace in aligned_traces:
        if trace["cost"] != trace["internal_cost"]:
            print(trace)
            pass
    print(bb - aa)
    print(sum(x["visited_states"] for x in aligned_traces))
    print(sum(x["cost"] // 10000 for x in aligned_traces))
    gviz = visualizer.apply(dfg, activities_count=ac, parameters={"start_activities": sa, "end_activities": ea,
                                                                  "format": "svg"})
    visualizer.view(gviz)
    cc = time.time()
    aligned_traces2 = petri_alignments.apply(log, net, im, fm,
                                             variant=petri_alignments.Variants.VERSION_DIJKSTRA_LESS_MEMORY)
    dd = time.time()
    print(dd - cc)
    print(sum(x["visited_states"] for x in aligned_traces2))
    print(sum(x["cost"] // 10000 for x in aligned_traces2))


if __name__ == "__main__":
    execute_script()
