import pm4py
import os
from pm4py.algo.discovery.dfg.adapters.pandas import df_statistics
from pm4py.visualization.dfg import visualizer as dfg_visualizer


def execute_script():
    log = pm4py.read_xes(os.path.join("..", "tests", "input_data", "roadtraffic100traces.xes"), return_legacy_log_object=False)
    cost_based_dfg = df_statistics.get_dfg_graph(log, measure="cost", cost_attribute="amount")
    gviz = dfg_visualizer.apply(cost_based_dfg, variant=dfg_visualizer.Variants.COST, parameters={"format": "svg"})
    dfg_visualizer.view(gviz)


if __name__ == "__main__":
    execute_script()
