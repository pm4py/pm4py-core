import os
from pm4py.algo.discovery.inductive import algorithm as inductive
from pm4py.objects.log.importer.xes import importer as xes_importer
from pm4py.objects.process_tree.process_tree import ProcessTree
from pm4py.visualization.process_tree import visualizer as pt_vis
from pm4py.algo.conformance.tree_alignments import algorithm as align_approx
from pm4py.objects.petri.align_utils import pretty_print_alignments


def execute_script():
    log_path = os.path.join("..", "tests", "input_data", "running-example.xes")

    log = xes_importer.apply(log_path)
    tree: ProcessTree = inductive.apply_tree(log)
    gviz = pt_vis.apply(tree, parameters={pt_vis.Variants.WO_DECORATION.value.Parameters.FORMAT: "svg"})
    pt_vis.view(gviz)

    print("start calculate approximated alignments")
    approx_alignments = align_approx.apply(log, tree)
    pretty_print_alignments(approx_alignments)


if __name__ == "__main__":
    execute_script()
