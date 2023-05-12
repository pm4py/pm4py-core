import os
import pm4py
from pm4py.algo.organizational_mining.network_analysis import algorithm as network_analysis
from pm4py.visualization.network_analysis import visualizer as network_visualizer


def execute_script():
    log = pm4py.read_xes(os.path.join("..", "tests", "input_data", "receipt.xes"))

    # frequency view of the network analysis

    # OUT column: case identifier
    # IN column: case identifier (the next event having the same case identifier is matched)
    # NODE column: the attribute to use to classify the node. In this case, we use the org:group (organizational group)
    # EDGE column: the attribute (of the source event) to use to classify the edge. In this case, we use the
    # concept:name (activity)

    frequency_edges = pm4py.discover_network_analysis(log, out_column="case:concept:name", in_column="case:concept:name", node_column_source="org:group", node_column_target="org:group", edge_column="concept:name", performance=False)
    pm4py.view_network_analysis(frequency_edges, variant="frequency", format="svg", edge_threshold=10)

    # performance view of the network analysis

    # OUT column: case identifier
    # IN column: case identifier (the next event having the same case identifier is matched)
    # NODE column: the attribute to use to classify the node. In this case, we use the org:group (organizational group)
    # EDGE column: the attribute (of the source event) to use to classify the edge. In this case, we use the
    # concept:name (activity)

    performance_edges = pm4py.discover_network_analysis(log, out_column="case:concept:name", in_column="case:concept:name", node_column_source="org:group", node_column_target="org:group", edge_column="concept:name", performance=True)
    pm4py.view_network_analysis(performance_edges, variant="performance", format="svg", edge_threshold=10)

    resource_group_edges = pm4py.discover_network_analysis(log, out_column="case:concept:name", in_column="case:concept:name", node_column_source="org:resource", node_column_target="org:group", edge_column="org:resource", performance=False)
    pm4py.view_network_analysis(resource_group_edges, variant="frequency", format="svg", edge_threshold=10)


if __name__ == "__main__":
    execute_script()
