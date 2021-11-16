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

    frequency_edges = network_analysis.apply(log, parameters={"in_column": "case:concept:name",
                                                              "out_column": "case:concept:name",
                                                              "node_column": "org:group", "edge_column": "concept:name",
                                                              "include_performance": False})
    gviz_frequency = network_visualizer.apply(frequency_edges, variant=network_visualizer.Variants.FREQUENCY,
                                              parameters={"edge_threshold": 10, "format": "svg"})
    network_visualizer.view(gviz_frequency)

    # performance view of the network analysis

    # OUT column: case identifier
    # IN column: case identifier (the next event having the same case identifier is matched)
    # NODE column: the attribute to use to classify the node. In this case, we use the org:group (organizational group)
    # EDGE column: the attribute (of the source event) to use to classify the edge. In this case, we use the
    # concept:name (activity)

    performance_edges = network_analysis.apply(log, parameters={"in_column": "case:concept:name",
                                                                "out_column": "case:concept:name",
                                                                "node_column": "org:group",
                                                                "edge_column": "concept:name",
                                                                "include_performance": True})
    gviz_performance = network_visualizer.apply(performance_edges, variant=network_visualizer.Variants.PERFORMANCE,
                                                parameters={"edge_threshold": 10, "format": "svg",
                                                            "aggregation_measure": "median"})
    network_visualizer.view(gviz_performance)


if __name__ == "__main__":
    execute_script()
