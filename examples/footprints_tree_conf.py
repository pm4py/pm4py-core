from pm4py.objects.log.importer.xes import importer as xes_importer
from pm4py.algo.discovery.inductive import algorithm as inductive_miner
from pm4py.algo.discovery.footprints import algorithm as fp_discovery
from pm4py.algo.conformance.footprints import algorithm as fp_conformance
from pm4py.algo.conformance.footprints.util import tree_visualization
from pm4py.visualization.process_tree import visualizer as pt_visualizer
from pm4py.statistics.traces.log import case_statistics
from pm4py.algo.filtering.log.variants import variants_filter
from pm4py.algo.discovery.dfg import algorithm as dfg_discovery
from pm4py.algo.filtering.log.paths import paths_filter
from pm4py.util.vis_utils import human_readable_stat
from pm4py.algo.filtering.log.variants import variants_filter
from copy import deepcopy
import os


def execute_script():
    log = xes_importer.apply(os.path.join("..", "tests", "input_data", "receipt.xes"))
    throughput_time = case_statistics.get_median_caseduration(log)
    variants, variants_times = variants_filter.get_variants_along_with_case_durations(log)
    dfg = dfg_discovery.apply(log)
    filtered_log = variants_filter.apply_auto_filter(deepcopy(log))
    # filtered_log = log
    tree = inductive_miner.apply_tree(filtered_log)
    fp_log = fp_discovery.apply(log, variant=fp_discovery.Variants.ENTIRE_EVENT_LOG)
    fp_model = fp_discovery.apply(tree)
    conf = fp_conformance.apply(fp_log, fp_model)
    conf_occ = sorted([(x, dfg[x]) for x in conf], key=lambda y: (y[1], y[0][0], y[0][1]), reverse=True)
    print(
        "source activity\t\ttarget activity\t\toccurrences\t\tthroughput time log\t\tthroughput time traces with path")
    for i in range(min(10, len(conf_occ))):
        path = conf_occ[i][0]
        occ = conf_occ[i][1]
        red_log = paths_filter.apply(log, [path])
        red_throughput_time = case_statistics.get_median_caseduration(red_log)
        print("%s\t\t%s\t\t%d\t\t%s\t\t%s" % (
            path[0], path[1], occ, human_readable_stat(throughput_time), human_readable_stat(red_throughput_time)))
    variants_length = sorted([(x, len(variants[x])) for x in variants.keys()], key=lambda y: (y[1], y[0]), reverse=True)
    print("\nvariant\t\toccurrences\t\tthroughput time log\t\tthroughput time traces with path")
    for i in range(min(10, len(variants_length))):
        var = variants_length[i][0]
        vark = str(var)
        if len(vark) > 10:
            vark = vark[:10]
        occ = variants_length[i][1]
        fp_log_var = fp_discovery.apply(variants[var], variant=fp_discovery.Variants.ENTIRE_EVENT_LOG)
        conf_var = fp_conformance.apply(fp_log_var, fp_model)
        is_fit = str(len(conf_var) == 0)
        var_throughput = case_statistics.get_median_caseduration(variants[var])
        print("%s\t\t%d\t\t%s\t\t%s\t\t%s" % (vark, occ, is_fit, throughput_time, human_readable_stat(var_throughput)))

    # print(conf_occ)
    conf_colors = tree_visualization.apply(tree, conf)
    if True:
        gviz = pt_visualizer.apply(tree, parameters={"format": "svg",
                                                     pt_visualizer.Variants.WO_DECORATION.value.Parameters.COLOR_MAP: conf_colors,
                                                     pt_visualizer.Variants.WO_DECORATION.value.Parameters.ENABLE_DEEPCOPY: False})
        pt_visualizer.view(gviz)


if __name__ == "__main__":
    execute_script()
