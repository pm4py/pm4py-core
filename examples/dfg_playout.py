import pm4py
from pm4py.objects.dfg.filtering import dfg_filtering
from pm4py.objects.dfg.utils import dfg_playout
import os


def execute_script():
    log = pm4py.read_xes(os.path.join("..", "tests", "input_data", "receipt.xes"))
    activities = pm4py.get_attribute_values(log, "concept:name")
    dfg, sa, ea = pm4py.discover_dfg(log)
    # filters the DFG to make a simpler one
    perc = 0.5
    dfg, sa, ea, activities = dfg_filtering.filter_dfg_on_activities_percentage(dfg, sa, ea, activities, perc)
    dfg, sa, ea, activities = dfg_filtering.filter_dfg_on_paths_percentage(dfg, sa, ea, activities, perc)
    # creates the simulated log
    simulated_log = dfg_playout.apply(dfg, sa, ea)
    print(simulated_log)
    print(len(simulated_log))
    print(sum(x.attributes["probability"] for x in simulated_log))
    # shows the two DFGs to show that they are identical
    pm4py.view_dfg(dfg, sa, ea, log=log, format="svg")
    new_dfg, new_sa, new_ea = pm4py.discover_dfg(simulated_log)
    pm4py.view_dfg(new_dfg, new_sa, new_ea, log=simulated_log, format="svg")
    for trace in simulated_log:
        print(list(x["concept:name"] for x in trace))
        print(trace.attributes["probability"], dfg_playout.get_trace_probability(trace, dfg, sa, ea))
        break
    dfg, sa, ea = pm4py.discover_dfg(log)
    variants = pm4py.get_variants(log)
    sum_prob_log_variants = 0.0
    for var in variants:
        sum_prob_log_variants += dfg_playout.get_trace_probability(variants[var][0], dfg, sa, ea)
    print("percentage of behavior allowed from DFG that is in the log (from 0.0 to 1.0): ", sum_prob_log_variants)


if __name__ == "__main__":
    execute_script()
