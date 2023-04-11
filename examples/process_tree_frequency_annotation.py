import pm4py
import os
from pm4py.algo.conformance.alignments.process_tree.util import search_graph_pt_frequency_annotation
from pm4py.visualization.process_tree import visualizer as pt_visualizer


def execute_script():
    log = pm4py.read_xes(os.path.join("..", "tests", "input_data", "receipt.xes"))
    tree = pm4py.discover_process_tree_inductive(log)
    aligned_traces = pm4py.conformance_diagnostics_alignments(log, tree, return_diagnostics_dataframe=False)
    tree = search_graph_pt_frequency_annotation.apply(tree, aligned_traces)
    gviz = pt_visualizer.apply(tree, parameters={"format": "svg"}, variant=pt_visualizer.Variants.FREQUENCY_ANNOTATION)
    pt_visualizer.view(gviz)


if __name__ == "__main__":
    execute_script()
