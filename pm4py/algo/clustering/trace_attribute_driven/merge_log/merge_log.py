from functools import reduce
from scipy.cluster.hierarchy import fcluster
from pm4py.algo.clustering.trace_attribute_driven.util import filter_subsets
from pm4py.objects.log.importer.xes import importer as xes_importer
from pm4py.objects.log.log import EventLog
from pm4py.util import constants


def merge_log(path, cate, iter):
    loglist = []
    mergedlog = EventLog()

    for i in range(1, cate + 1):
        for j in range(1, iter + 1):
            log = xes_importer.apply(path + '\\log_1_' + str(i) + '_' + str(j) + ".xes")
            for trace in log:
                trace.attributes["concept:name"] = str(iter * (i - 1) + j)
                trace.attributes["index"] = str(iter * (i - 1) + j)
            loglist.append(log)

    for i in range(len(loglist)):
        for trace in loglist[i]:
            mergedlog.append(trace)

    return loglist, mergedlog


def update_merge(loglist):
    mergedlog = EventLog()

    for i in range(len(loglist)):
        for trace in loglist[i]:
            mergedlog.append(trace)
    return mergedlog


# this is for single string
def log2sublog(log, string, KEY):
    tracefilter_log = filter_subsets.apply_trace_attributes(log, [string],
                                                            parameters={
                                                                constants.PARAMETER_CONSTANT_ATTRIBUTE_KEY: KEY,
                                                                "positive": True})

    return tracefilter_log


# this is for string list
def logslice(log, str_list, KEY):
    tracefilter_log = filter_subsets.apply_trace_attributes(log, str_list,
                                                            parameters={
                                                                constants.PARAMETER_CONSTANT_ATTRIBUTE_KEY: KEY,
                                                                "positive": True})

    return tracefilter_log


# Create a nested dictionary from the ClusterNode's returned by SciPy
def add_node(node, parent):
    # First create the new node and append it to its parent's children
    newNode = dict(node_id=node.id, children=[])
    parent["children"].append(newNode)

    # Recursively add the current node's children
    if node.left: add_node(node.left, newNode)
    if node.right: add_node(node.right, newNode)


# Label each node with the names of each leaf in its subtree
def label_tree(n, id2name):
    # flatten_tree=[]
    # If the node is a leaf, then we have its name
    if len(n["children"]) == 0:
        leafNames = [id2name[n["node_id"]]]

    # If not, flatten all the leaves in the node's subtree
    else:
        leafNames = reduce(lambda ls, c: ls + label_tree(c, id2name), n["children"], [])

    # Delete the node id since we don't need it anymore and
    # it makes for cleaner JSON
    del n["node_id"]

    # Labeling convention: "-"-separated leaf names
    n["name"] = name = "-".join(sorted(map(str, leafNames)))

    return leafNames


def clusteredlog(Z, maxclust, list_of_vals, log, METHOD, ATTR_NAME):
    clu_index = fcluster(Z, maxclust, criterion='maxclust')
    clu_index = dict(zip(list_of_vals, clu_index))
    clu_list_log = []
    clu_list = []
    for i in range(maxclust):
        temp = [key for key, value in clu_index.items() if value == i + 1]
        clu_list.append(temp)
        logtemp = logslice(log, temp, ATTR_NAME)
        clu_list_log.append(logtemp)
    return clu_list_log, clu_list
