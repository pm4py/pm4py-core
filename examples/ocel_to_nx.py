import pm4py
import networkx as nx
import os


def execute_script():
    ocel = pm4py.read_ocel("../tests/input_data/ocel/example_log.jsonocel")
    nx_digraph = pm4py.convert_ocel_to_networkx(ocel)
    nx.write_gexf(nx_digraph, "converted_graph.gexf")
    os.remove("converted_graph.gexf")


if __name__ == "__main__":
    execute_script()
