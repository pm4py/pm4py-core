import pm4py
from pm4py.visualization.networkx import visualizer as nx_to_gv_vis
from examples import examples_conf


def execute_script():
    log = pm4py.read_xes("../tests/input_data/running-example.xes")
    # gets an 'event graph' where events, cases and their relationships
    # are represented in a graph (NetworkX DiGraph)
    event_graph = pm4py.convert_log_to_networkx(log)

    # visualize the NX DiGraph using Graphviz
    gviz = nx_to_gv_vis.apply(event_graph, parameters={"format": examples_conf.TARGET_IMG_FORMAT})
    nx_to_gv_vis.view(gviz)


if __name__ == "__main__":
    execute_script()
