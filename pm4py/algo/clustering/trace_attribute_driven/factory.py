import deprecation
from scipy.cluster.hierarchy import to_tree, linkage
from pm4py.statistics.attributes.log import get as attributes_filter
from pm4py.algo.clustering.trace_attribute_driven.merge_log import merge_log
from pm4py.algo.clustering.trace_attribute_driven.util import evaluation
from pm4py.objects.conversion.log import converter as log_converter

VARIANT_DMM_LEVEN = "variant_DMM_leven"
VARIANT_AVG_LEVEN = "variant_avg_leven"
VARIANT_DMM_VEC = "variant_DMM_vec"
VARIANT_AVG_VEC = "variant_avg_vec"
DFG = 'dfg'

VERSION_METHODS = {VARIANT_DMM_LEVEN: evaluation.eval_DMM_leven, VARIANT_AVG_LEVEN: evaluation.eval_avg_leven,
                   VARIANT_DMM_VEC: evaluation.eval_DMM_variant, VARIANT_AVG_VEC: evaluation.eval_avg_variant,
                   DFG: evaluation.dfg_dis}


@deprecation.deprecated(deprecated_in='1.3.0', removed_in='2.0.0', current_version='',
                        details='Use algorithm entrypoint instead (clustering/trace_attribute_driven/factory)')
def bfs(tree):
    queue = []
    output = []
    queue.append(tree)
    while queue:
        # element in queue is waiting to become root and splited into child
        # root is the first ele of queue
        root = queue.pop(0)
        if len(root['children']) > 0:
            name = [root['name']]
            for child in root['children']:
                queue.append(child)
                name.append(child['name'])
            output.append(name)

    return output


@deprecation.deprecated(deprecated_in='1.3.0', removed_in='2.0.0', current_version='',
                        details='Use algorithm entrypoint instead (clustering/trace_attribute_driven/factory)')
def apply(log, trace_attribute, variant=VARIANT_DMM_LEVEN, parameters=None):
    """
    Apply the hierarchical clustering to a log starting from a trace attribute.

    MSc Thesis is available at: https://www.pads.rwth-aachen.de/global/show_document.asp?id=aaaaaaaaalpxgft&download=1
    Defense slides are available at: https://www.pads.rwth-aachen.de/global/show_document.asp?id=aaaaaaaaalpxgqx&download=1

    Parameters
    ----------------
    log
        Log
    trace_attribute
        Trace attribute to exploit for the clustering
    variant
        Variant of the algorithm to apply, possible values:
        - variant_DMM_leven (that is the default)
        - variant_avg_leven
        - variant_DMM_vec
        - variant_avg_vec
        - dfg

    Returns
    -----------------
    tree
        Hierarchical cluster tree
    leafname
        Root node
    """
    if parameters is None:
        parameters = {}

    log = log_converter.apply(log, parameters=parameters)

    percent = 1
    alpha = 0.5

    list_of_vals = []
    list_log = []
    list_of_vals_dict = attributes_filter.get_trace_attribute_values(log, trace_attribute)

    list_of_vals_keys = list(list_of_vals_dict.keys())
    for i in range(len(list_of_vals_keys)):
        list_of_vals.append(list_of_vals_keys[i])

    for i in range(len(list_of_vals)):
        logsample = merge_log.log2sublog(log, list_of_vals[i], trace_attribute)
        list_log.append(logsample)

    if variant in VERSION_METHODS:
        y = VERSION_METHODS[variant](list_log, percent, alpha)

    Z = linkage(y, method='average')

    # Create dictionary for labeling nodes by their IDs

    id2name = dict(zip(range(len(list_of_vals)), list_of_vals))

    T = to_tree(Z, rd=False)
    d3Dendro = dict(children=[], name="Root1")
    merge_log.add_node(T, d3Dendro)

    leafname = merge_log.label_tree(d3Dendro["children"][0], id2name)
    d3Dendro = d3Dendro["children"][0]
    d3Dendro["name"] = 'root'
    tree = d3Dendro

    trilist = bfs(tree)
    trilist[0][0] = trilist[0][1] + '-' + trilist[0][2]

    rootlist = []
    for ele in trilist:
        rootlist.append(ele[0])

    return tree, leafname
