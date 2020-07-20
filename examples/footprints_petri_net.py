from pm4py.objects.log.importer.xes import importer
from pm4py.algo.filtering.log.variants import variants_filter
from pm4py.algo.discovery.inductive import factory as inductive_miner
from pm4py.objects.conversion.process_tree import converter
from pm4py.algo.discovery.footprints import algorithm as footprints_discovery
from pm4py.algo.conformance.footprints import algorithm as footprints_conformance
from pm4py.visualization.footprints import visualizer as fp_visualizer
import os
from copy import deepcopy


def execute_script():
    # import a log
    log = importer.apply(os.path.join("..", "tests", "input_data", "receipt.xes"))
    # found a filtered version of the log that is used to discover a process model
    filtered_log = variants_filter.apply_auto_filter(deepcopy(log))
    # discover a process tree using inductive miner
    tree = inductive_miner.apply_tree(filtered_log)
    print(tree)
    # apply the conversion of a process tree into a Petri net
    net, im, fm = converter.apply(tree)
    # Footprints discovery: discover a list of footprints
    # for all the cases of the log
    fp_log = footprints_discovery.apply(log)
    # discover the footpritns from the process tree
    fp_tree = footprints_discovery.apply(tree)
    # discover the footpritns from the Petri net
    fp_net = footprints_discovery.apply(net, im)
    print(len(fp_tree["sequence"]), len(fp_tree["parallel"]), len(fp_net["sequence"]), len(fp_net["parallel"]))
    print(fp_tree["sequence"] == fp_net["sequence"] and fp_tree["parallel"] == fp_net["parallel"])
    # apply the footprints conformance checking
    conf = footprints_conformance.apply(fp_log, fp_net)
    for trace_an in conf:
        if trace_an:
            # print the first anomalous trace (containing deviations
            # that are contained in the trace but not allowed by the model)
            print(trace_an)
            break
    # finds the footprints for the entire log (not case-by-case, but taking
    # the relations that appear inside the entire log)
    fp_log_entire = footprints_discovery.apply(log, variant=footprints_discovery.Variants.ENTIRE_EVENT_LOG)
    # visualize the footprint table
    gviz = fp_visualizer.apply(fp_log_entire, fp_net, parameters={"format": "svg"})
    fp_visualizer.view(gviz)


if __name__ == "__main__":
    execute_script()
