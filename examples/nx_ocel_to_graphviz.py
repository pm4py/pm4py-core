import pm4py
from pm4py.visualization.networkx import visualizer as nx_to_gv_vis
from examples import examples_conf


def execute_script():
    ocel = pm4py.read_ocel2("../tests/input_data/ocel/ocel20_example.jsonocel")

    # convers the OCEL to a NetworkX graph with events, objects, E2O, O2O, and object changes
    event_graph = pm4py.convert_ocel_to_networkx(ocel)

    # visualize the NX DiGraph using Graphviz
    gviz = nx_to_gv_vis.apply(event_graph, parameters={"format": examples_conf.TARGET_IMG_FORMAT})
    nx_to_gv_vis.view(gviz)


if __name__ == "__main__":
    execute_script()
