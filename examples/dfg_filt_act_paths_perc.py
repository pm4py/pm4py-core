import pm4py
from pm4py.visualization.dfg import visualizer as dfg_visualizer


def execute_script():
    log = pm4py.read_xes("../tests/input_data/receipt.xes")
    dfg, sa, ea = pm4py.discover_dfg(log)
    act_count = pm4py.get_attribute_values(log, "concept:name")
    # keep the specified amount of activities
    dfg, sa, ea, act_count = pm4py.objects.dfg.filtering.dfg_filtering.filter_dfg_on_activities_percentage(dfg, sa, ea, act_count, 0.3)
    # keep the specified amount of paths
    dfg, sa, ea, act_count = pm4py.objects.dfg.filtering.dfg_filtering.filter_dfg_on_paths_percentage(dfg, sa, ea, act_count, 0.3)
    # view the DFG
    gviz = dfg_visualizer.apply(dfg, activities_count=act_count, parameters={dfg_visualizer.Variants.FREQUENCY.value.Parameters.START_ACTIVITIES: sa,
                                                                             dfg_visualizer.Variants.FREQUENCY.value.Parameters.END_ACTIVITIES: ea,
                                                                             dfg_visualizer.Variants.FREQUENCY.value.Parameters.FORMAT: "svg"})
    dfg_visualizer.view(gviz)


if __name__ == "__main__":
    execute_script()
