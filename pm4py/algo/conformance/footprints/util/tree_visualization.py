from pm4py.algo.discovery.footprints.tree.variants import bottomup as bottomup_discovery
from pm4py.objects.process_tree import bottomup as bottomup_util
from pm4py.algo.discovery.footprints.outputs import Outputs

FP_DEV_COLOR = "red"


def apply(tree, conf_results, parameters=None):
    """
    Projects conformance results on top of the process tree

    Parameters
    --------------
    tree
        Process tree
    conf_results
        Conformance results (footprints on the entire log vs entire model)
    parameters
        Parameters of the algorithm

    Returns
    --------------
    color_map
        Color map to be provided to the visualization
    """
    if parameters is None:
        parameters = {}

    if type(conf_results) is list:
        raise Exception("the visualization can only be applied with total footprints (not trace-by-trace)!")

    bottomup_nodes = bottomup_util.get_bottomup_nodes(tree, parameters=parameters)
    labels_dictio = {x.label: x for x in bottomup_nodes if x.operator is None and x.label is not None}
    all_fp_dictio = bottomup_discovery.get_all_footprints(tree, parameters=parameters)
    conf_colors = {}

    for res in conf_results:
        if res[0] in labels_dictio and res[1] in labels_dictio:
            conf_colors[labels_dictio[res[0]]] = FP_DEV_COLOR
            conf_colors[labels_dictio[res[1]]] = FP_DEV_COLOR
            for n in bottomup_nodes:
                if res[0] in all_fp_dictio[n][Outputs.ACTIVITIES.value] and res[1] in all_fp_dictio[n][
                    Outputs.ACTIVITIES.value]:
                    conf_colors[n] = FP_DEV_COLOR
                    break

    return conf_colors
