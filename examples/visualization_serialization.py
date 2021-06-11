import pm4py
from pm4py.algo.discovery.transition_system import algorithm as ts_discovery
from pm4py.visualization.dfg import visualizer as dfg_visualizer
from pm4py.visualization.heuristics_net import visualizer as hn_visualizer
from pm4py.visualization.process_tree import visualizer as tree_visualizer
from pm4py.visualization.petri_net import visualizer as pn_visualizer
from pm4py.visualization.bpmn import visualizer as bpmn_visualizer
from pm4py.visualization.transition_system import visualizer as ts_visualizer
from pm4py.statistics.traces.generic.log import case_statistics
from pm4py.visualization.graphs import visualizer as graphs_visualizer


def execute_script():
    log = pm4py.read_xes("../tests/input_data/running-example.xes")
    dfg, sa, ea = pm4py.discover_dfg(log)
    tree = pm4py.discover_process_tree_inductive(log)
    heu_net = pm4py.discover_heuristics_net(log)
    net, im, fm = pm4py.discover_petri_net_alpha(log)
    bpmn = pm4py.convert_to_bpmn(tree)
    ts = ts_discovery.apply(log)
    x_cases, y_cases = case_statistics.get_kde_caseduration(log)

    gviz1 = dfg_visualizer.apply(dfg)
    gviz2 = tree_visualizer.apply(tree)
    gviz3 = hn_visualizer.apply(heu_net)
    gviz4 = pn_visualizer.apply(net, im, fm)
    gviz5 = bpmn_visualizer.apply(bpmn)
    gviz6 = ts_visualizer.apply(ts)
    gviz7 = graphs_visualizer.apply(x_cases, y_cases, variant=graphs_visualizer.Variants.CASES,
                                          parameters={graphs_visualizer.Variants.CASES.value.Parameters.FORMAT: "svg"})

    print("1", len(dfg_visualizer.serialize_dot(gviz1)))
    print("1", len(dfg_visualizer.serialize(gviz1)))
    print("2", len(tree_visualizer.serialize_dot(gviz2)))
    print("2", len(tree_visualizer.serialize(gviz2)))
    print("3", len(hn_visualizer.serialize(gviz3)))
    print("4", len(pn_visualizer.serialize_dot(gviz4)))
    print("4", len(pn_visualizer.serialize(gviz4)))
    print("5", len(bpmn_visualizer.serialize_dot(gviz5)))
    print("5", len(bpmn_visualizer.serialize(gviz5)))
    print("6", len(ts_visualizer.serialize_dot(gviz6)))
    print("6", len(ts_visualizer.serialize(gviz6)))
    print("7", len(graphs_visualizer.serialize(gviz7)))


if __name__ == "__main__":
    execute_script()
