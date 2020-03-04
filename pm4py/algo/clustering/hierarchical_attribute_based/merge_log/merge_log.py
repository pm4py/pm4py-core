import matplotlib.pyplot as plt
from functools import reduce
import pandas as pd
import numpy as np
import time
from collections import Counter
from scipy.cluster.hierarchy import dendrogram, linkage, to_tree, fcluster
from scipy.spatial.distance import squareform
from pm4py.algo.clustering.hierarchical_attribute_based.util import filter_subsets
from pm4py.objects.log.importer.xes import factory as xes_importer
from pm4py.algo.discovery.inductive import factory as inductive_miner
from pm4py.evaluation.replay_fitness import factory as replay_factory
from pm4py.evaluation.precision import factory as precision_factory
from pm4py.objects.log.log import EventLog
from pm4py.util import constants
from pm4py.algo.filtering.log.attributes import attributes_filter
from pm4py.algo.clustering.hierarchical_attribute_based.linkage_method import linkage_avg
from pm4py.algo.clustering.hierarchical_attribute_based.util import evaluation


def merge_log(path, cate, iter):
    '''
    modify the trace attribute for each log and then merge all fake sublogs into one log in order to use in WS
    :param path:
    :param cate:
    :param iter:
    :return:
    '''
    loglist = []
    mergedlog = EventLog()

    for i in range(1, cate + 1):
        for j in range(1, iter + 1):
            log = xes_importer.apply(path + '\\log_1_' + str(i) + '_' + str(j) + ".xes")
            for trace in log:
                trace.attributes["concept:name"] = str(iter * (i - 1) + j)
                trace.attributes["index"] = str(iter * (i - 1) + j)
            print(path + '\\log_1_' + str(i) + '_' + str(j) + ".xes")
            print(filter_subsets.sublog_percent(log, 1))
            loglist.append(log)

    for i in range(len(loglist)):
        for trace in loglist[i]:
            # print(trace)
            mergedlog.append(trace)

    return loglist, mergedlog


def update_merge(loglist):
    mergedlog = EventLog()

    for i in range(len(loglist)):
        for trace in loglist[i]:
            # print(trace)
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
    # flatten_tree.append(n)
    # print("flatree",flatten_tree)

    return leafNames


def get_dendrogram_svg(log, parameters=None):
    if parameters is None:
        parameters = {}

    cluster_avg = parameters["cluster_avg"] if "cluster_avg" in parameters else True

    percent = 1
    alpha = 0.5
    TYPE = 'index'

    list_of_vals = []
    list_log = []
    list_of_vals_dict = attributes_filter.get_trace_attribute_values(log, 'index')
    # ta = (attributes_filter.get_all_trace_attributes_from_log(log))
    # ea = (attributes_filter.get_all_event_attributes_from_log(log))
    # print(ta|ea)
    # print(list_of_vals_dict.keys())
    list_of_vals_keys = list(list_of_vals_dict.keys())
    for i in range(len(list_of_vals_keys)):
        list_of_vals.append(list_of_vals_keys[i])

    for i in range(len(list_of_vals)):
        logsample = log2sublog(log, list_of_vals[i], TYPE)
        list_log.append(logsample)

    if (cluster_avg):
        y = evaluation.eval_avg_leven(list_log, percent, alpha)
    else:
        y = evaluation.eval_DMM_leven(list_log, percent, alpha)

    Z = linkage(y, method='average')

    # Create dictionary for labeling nodes by their IDs

    id2name = dict(zip(range(len(list_of_vals)), list_of_vals))

    T = to_tree(Z, rd=False)
    d3Dendro = dict(children=[], name="Root1")
    add_node(T, d3Dendro)

    label_tree(d3Dendro["children"][0], id2name)
    d3Dendro = d3Dendro["children"][0]
    d3Dendro["name"] = 'root'
    ret = d3Dendro
    print(ret)

    # plt.figure(figsize=(10, 8))
    # # dn = fancy_dendrogram(Z, max_d=0.35)
    # dn = dendrogram(Z, labels=list_of_vals)
    # # dn = dendrogram(Z,labels=np.array(list_of_vals))
    # plt.title('Hierarchical Clustering Dendrogram')
    # # plt.xlabel('Loan Amount')
    # plt.ylabel('Distance')
    # plt.savefig('cluster.svg')
    # plt.show()


def clusteredlog(Z, maxclust, list_of_vals, log, METHOD, ATTR_NAME):
    clu_index = fcluster(Z, maxclust, criterion='maxclust')
    clu_index = dict(zip(list_of_vals, clu_index))
    print('clu_index',clu_index)
    clu_list_log = []
    clu_list = []
    for i in range(maxclust):
        temp = [key for key, value in clu_index.items() if value == i + 1]
        print([i, temp])
        clu_list.append(temp)
        logtemp = logslice(log, temp, ATTR_NAME)
        clu_list_log.append(logtemp)
        # if (maxclust > 1):
        #     filename = 'D:/Sisc/19SS/thesis/Dataset/' + 'log' + '_' + str(
        #         maxclust) + '_' + str(i) + '_' + METHOD + ATTR_NAME + '.xes'
        #     # filename = '/home/yukun/resultlog/Receipt/' + ATTR_NAME + '/' + 'log' + '_' + str(
        #     #     maxclust) + '_' + str(i) + '_' + METHOD + ATTR_NAME + '.xes'
        #     xes_exporter.export_log(logtemp, filename)
    return clu_list_log, clu_list


def main_calc_leven_recompute(log, ATTR_NAME, METHOD, TYPE, PIC_PATH, percent, alpha,runtime,plot_clu):
    '''
    using levenshtein method without recomputing to get fitness, precision and F1-score of all cluster steps
    :param log:
    :param ATTR_NAME:
    :param METHOD:
    :param TYPE:
    :param percent:
    :param alpha:
    :param runtime:
    :param plot_clu:
    :return:
    '''
    list_of_vals = []
    list_log = []
    list_of_vals_dict = attributes_filter.get_trace_attribute_values(log, ATTR_NAME)

    list_of_vals_keys = list(list_of_vals_dict.keys())
    for i in range(len(list_of_vals_keys)):
        list_of_vals.append(list_of_vals_keys[i])

    print(list_of_vals)
    for i in range(len(list_of_vals)):
        logsample = log2sublog(log, list_of_vals[i], ATTR_NAME)
        list_log.append(logsample)
    print(len(list_log))

    # DFG test
    start = time.time()
    if METHOD == 'dfg':
        print("dfg is using!")
        y = evaluation.dfg_dis(list_log, percent, alpha)
        dist_mat = squareform(y)
        Z = linkage_avg.linkage_dfg_update(list_log, dist_mat, alpha, percent)
    elif METHOD == 'DMM':
        print("DMM is using!")
        y = evaluation.eval_DMM_leven(list_log, percent, alpha)
        dist_mat = squareform(y)
        Z = linkage_avg.linkage_DMM_update_leven(list_log, dist_mat, alpha, percent)
    elif METHOD == 'avg':
        print("avg is using!")
        y = evaluation.eval_avg_leven(list_log, percent, alpha)
        dist_mat = squareform(y)
        Z = linkage_avg.linkage_avg(list_log, dist_mat, alpha, percent)
    # print(y)
    # Z = linkage(y, method='average')


    end = time.time()
    runtime[TYPE] = end - start
    # print(Z)
    print("runtime" + TYPE, runtime[TYPE])

    fig = plt.figure(figsize=(12, 10))
    dn = dendrogram(Z, labels=np.array(list_of_vals))
    # plt.title('Hierarchical Clustering Dendrogram')
    plt.xlabel(ATTR_NAME)
    plt.ylabel('Distance')
    plt.savefig(PIC_PATH + 'cluster_wupdate' + '_' + TYPE + '.svg')

    # clu_index = fcluster(Z, 0.005, criterion='distance')
    # clu_index = dict(zip(list_of_vals, clu_index))
    # print('clu_index', clu_index)
    # clu_list_log5, clu_list5 = clusteredlog(Z, 6, list_of_vals, log, METHOD, ATTR_NAME)
    # clu_list_log6, clu_list6 = clusteredlog(Z, 7, list_of_vals, log, METHOD, ATTR_NAME)
    # clu_list_log7, clu_list7 = clusteredlog(Z, 8, list_of_vals, log, METHOD, ATTR_NAME)

    plot_fit = dict()
    plot_prec = dict()
    plot_F1 = dict()
    plot_box = dict()
    plot_box2 = dict()
    plot_boxfit = dict()
    plot_boxprec = dict()
    plot_length = []
    clu_list_dict = dict()
    length_li = []
    fit_li = []
    prec_li = []
    F1_li = []
    for i in range(1, plot_clu + 1):
        if i == 1:
            inductive_petri, inductive_initial_marking, inductive_final_marking = inductive_miner.apply(log)
            fitness = replay_factory.apply(log, inductive_petri, inductive_initial_marking,
                                           inductive_final_marking, variant="alignments")['averageFitness']

            precision = precision_factory.apply(log, inductive_petri, inductive_initial_marking,
                                                inductive_final_marking)
            # fitness, precision = get_fit_prec_hpc(log, log)
            F1 = 2 * fitness * precision / (fitness + precision)
            print("fit", fitness)
            print("prec", precision)
            plot_fit[str(i)] = fitness
            plot_prec[str(i)] = precision
            plot_F1[str(i)] = F1
            # plot_box[str(i)] = pd.Series(F1)
            plot_boxfit[str(i)] = fitness
            plot_boxprec[str(i)] = precision
            plot_box[str(i)] = F1
            plot_length.append([len(log)])
            tempclu_list_log = [list_log]
            tempclu_list = [list_of_vals]
        else:
            # print("tempclu_list",tempclu_list)
            clu_list_log, clu_list = clusteredlog(Z, i, list_of_vals, log, METHOD, ATTR_NAME)
            # length_li = []
            # fit_li = []
            # prec_li = []
            # F1_li = []
            # for j in range(0, i):
            #     length = len(clu_list_log[j])
            #     if length != 0:
            #         inductive_petri, inductive_initial_marking, inductive_final_marking = inductive_miner.apply(
            #             clu_list_log[j])
            #         fitness = replay_factory.apply(log, inductive_petri, inductive_initial_marking,
            #                                        inductive_final_marking, variant="alignments")['averageFitness']
            #         precision = precision_factory.apply(log, inductive_petri, inductive_initial_marking,
            #                                             inductive_final_marking)
            #         # fitness, precision = get_fit_prec_hpc(clu_list_log[j], log)
            #         F1 = 2 * fitness * precision / (fitness + precision)
            #         # individual info for each sublog
            #         length_li.append(length)
            #         fit_li.append(fitness)
            #         prec_li.append(precision)
            #         F1_li.append(F1)

            if len(clu_list_log[-1]) != 0:
                # print("lenclu_list_log",len(clu_list_log))
                diff = [item for item in clu_list if not item in tempclu_list]
                diff_old = [item for item in tempclu_list if not item in clu_list]
                # print("diff",diff)
                # print("diff_old", diff_old)
                tempclu_list.append(clu_list[clu_list.index(diff[0])])
                tempclu_list.append(clu_list[clu_list.index(diff[1])])
                # print(tempclu_list)

                tempclu_list_log.append(clu_list_log[clu_list.index(diff[0])])
                tempclu_list_log.append(clu_list_log[clu_list.index(diff[1])])
                # print(len(tempclu_list_log))
                if (len(diff)>2):
                    for k in range(0,len(diff)-2):
                        tempclu_list.append(clu_list[clu_list.index(diff[2+k])])
                        tempclu_list_log.append(clu_list_log[clu_list.index(diff[2+k])])

                del tempclu_list_log[tempclu_list.index(diff_old[0])]
                # print("del",len(tempclu_list_log))
                # clu_list_dict[str(i)] = clu_list

                for j in range(0, len(diff)):
                    length = len(clu_list_log[clu_list.index(diff[j])])
                    inductive_petri, inductive_initial_marking, inductive_final_marking = inductive_miner.apply(
                        clu_list_log[clu_list.index(diff[j])])
                    fitness = replay_factory.apply(log, inductive_petri, inductive_initial_marking,
                                                   inductive_final_marking, variant="alignments")['averageFitness']
                    precision = precision_factory.apply(log, inductive_petri, inductive_initial_marking,
                                                        inductive_final_marking)
                    # fitness, precision = get_fit_prec_hpc(clu_list_log[clu_list.index(diff[j])],log)
                    F1 = 2 * fitness * precision / (fitness + precision)
                    # individual info for each sublog
                    length_li.append(length)
                    fit_li.append(fitness)
                    prec_li.append(precision)
                    F1_li.append(F1)

                # print("fit", fit_li)
                # print("prec", prec_li)
                if (i > 2):
                    del length_li[tempclu_list.index(diff_old[0])]
                    del fit_li[tempclu_list.index(diff_old[0])]
                    del prec_li[tempclu_list.index(diff_old[0])]
                    del F1_li[tempclu_list.index(diff_old[0])]
                del tempclu_list[tempclu_list.index(diff_old[0])]
            # print("del", tempclu_list)

            # print('length',length_li)
            print("fit", fit_li)
            print("prec", prec_li)
            print("F1", F1_li)

            plot_fit[str(i)] = np.average(fit_li)
            plot_prec[str(i)] = np.average(prec_li)
            plot_F1[str(i)] = np.average(F1_li)
            # plot_box[str(i)] = pd.Series(F1_li)
            plot_boxfit[str(i)] = fit_li[::]
            plot_boxprec[str(i)] = prec_li[::]
            plot_box[str(i)] = F1_li[::]
            # length_licopy = length_li[::]
            plot_length.append(length_li[::])
            print('plot_length', plot_length)
            print("plot_fit", plot_fit)
            print("plot_prec", plot_prec)
            print("plot_F1", plot_F1)

    print("plot_fit", plot_fit)
    print("plot_prec", plot_prec)
    print("plot_F1", plot_F1)
    print('length', plot_length)
    print('plot_box', plot_box)
    print('plot_boxfit', plot_boxfit)
    print('plot_boxprec', plot_boxprec)

    return plot_fit, plot_prec, plot_F1,plot_boxfit,plot_boxprec,plot_box,plot_length,runtime

def main_calc_recompute(log, ATTR_NAME, METHOD, TYPE, PIC_PATH, percent, alpha,runtime,plot_clu):
    '''
    using feature vector method with recomputing to get fitness, precision and F1-score of all cluster steps
    :param log:
    :param ATTR_NAME:
    :param METHOD:
    :param TYPE:
    :param percent:
    :param alpha:
    :param runtime:
    :param plot_clu:
    :return:
    '''
    list_of_vals = []
    list_log = []
    list_of_vals_dict = attributes_filter.get_trace_attribute_values(log, ATTR_NAME)

    list_of_vals_keys = list(list_of_vals_dict.keys())
    for i in range(len(list_of_vals_keys)):
        list_of_vals.append(list_of_vals_keys[i])

    print(list_of_vals)
    for i in range(len(list_of_vals)):
        logsample = log2sublog(log, list_of_vals[i], ATTR_NAME)
        list_log.append(logsample)
    print(len(list_log))

    # DFG test
    start = time.time()
    if METHOD == 'dfg':
        print("dfg is using!")
        y = evaluation.dfg_dis(list_log, percent, alpha)
        dist_mat = squareform(y)
        Z = linkage_avg.linkage_dfg_update(list_log, dist_mat, alpha, percent)
    elif METHOD == 'DMM':
        print("DMM is using!")
        y = evaluation.eval_DMM_variant(list_log, percent, alpha)
        dist_mat = squareform(y)
        Z = linkage_avg.linkage_DMM_update(list_log, dist_mat, alpha, percent)
    elif METHOD == 'avg':
        print("avg is using!")
        y = evaluation.eval_avg_variant(list_log, percent, alpha)
        dist_mat = squareform(y)
        Z = linkage_avg.linkage_avg(list_log, dist_mat, alpha, percent)
    # print(y)
    # Z = linkage(y, method='average')


    end = time.time()
    runtime[TYPE] = end - start
    # print(Z)
    print("runtime" + TYPE, runtime[TYPE])

    fig = plt.figure(figsize=(12, 10))
    dn = dendrogram(Z, labels=np.array(list_of_vals))
    # plt.title('Hierarchical Clustering Dendrogram')
    plt.xlabel(ATTR_NAME)
    plt.ylabel('Distance')
    plt.savefig(PIC_PATH + 'cluster_wupdate' + '_' + TYPE + '.svg')

    plot_fit = dict()
    plot_prec = dict()
    plot_F1 = dict()
    plot_box = dict()
    plot_box2 = dict()
    plot_boxfit = dict()
    plot_boxprec = dict()
    plot_length = []
    clu_list_dict = dict()
    length_li = []
    fit_li = []
    prec_li = []
    F1_li = []
    for i in range(1, plot_clu + 1):
        if i == 1:
            inductive_petri, inductive_initial_marking, inductive_final_marking = inductive_miner.apply(log)
            fitness = replay_factory.apply(log, inductive_petri, inductive_initial_marking,
                                           inductive_final_marking, variant="alignments")['averageFitness']

            precision = precision_factory.apply(log, inductive_petri, inductive_initial_marking,
                                                inductive_final_marking)
            # fitness, precision = get_fit_prec_hpc(log, log)
            F1 = 2 * fitness * precision / (fitness + precision)
            print("fit", fitness)
            print("prec", precision)
            plot_fit[str(i)] = fitness
            plot_prec[str(i)] = precision
            plot_F1[str(i)] = F1
            # plot_box[str(i)] = pd.Series(F1)
            plot_boxfit[str(i)] = fitness
            plot_boxprec[str(i)] = precision
            plot_box[str(i)] = F1
            plot_length.append([len(log)])
            tempclu_list_log = [list_log]
            tempclu_list = [list_of_vals]
        else:
            # print("tempclu_list",tempclu_list)
            clu_list_log, clu_list = clusteredlog(Z, i, list_of_vals, log, METHOD, ATTR_NAME)
            # length_li = []
            # fit_li = []
            # prec_li = []
            # F1_li = []
            # for j in range(0, i):
            #     length = len(clu_list_log[j])
            #     if length != 0:
            #         # inductive_petri, inductive_initial_marking, inductive_final_marking = inductive_miner.apply(
            #         #     clu_list_log[j])
            #         # fitness = replay_factory.apply(log, inductive_petri, inductive_initial_marking,
            #         #                                inductive_final_marking, variant="alignments")['averageFitness']
            #         # precision = precision_factory.apply(log, inductive_petri, inductive_initial_marking,
            #         #                                     inductive_final_marking)
            #         fitness, precision = get_fit_prec_hpc(clu_list_log[j], log)
            #         F1 = 2 * fitness * precision / (fitness + precision)
            #         # individual info for each sublog
            #         length_li.append(length)
            #         fit_li.append(fitness)
            #         prec_li.append(precision)
            #         F1_li.append(F1)

            if len(clu_list_log[-1]) != 0:
                # print("lenclu_list_log",len(clu_list_log))
                diff = [item for item in clu_list if not item in tempclu_list]
                diff_old = [item for item in tempclu_list if not item in clu_list]
                # print("diff",diff)
                # print("diff_old", diff_old)
                tempclu_list.append(clu_list[clu_list.index(diff[0])])
                tempclu_list.append(clu_list[clu_list.index(diff[1])])
                # print(tempclu_list)

                tempclu_list_log.append(clu_list_log[clu_list.index(diff[0])])
                tempclu_list_log.append(clu_list_log[clu_list.index(diff[1])])
                # print(len(tempclu_list_log))
                if (len(diff) > 2):
                    for k in range(0, len(diff) - 2):
                        tempclu_list.append(clu_list[clu_list.index(diff[2 + k])])
                        tempclu_list_log.append(clu_list_log[clu_list.index(diff[2 + k])])

                del tempclu_list_log[tempclu_list.index(diff_old[0])]
                # print("del",len(tempclu_list_log))
                # clu_list_dict[str(i)] = clu_list

                for j in range(0, len(diff)):
                    length = len(clu_list_log[clu_list.index(diff[j])])
                    inductive_petri, inductive_initial_marking, inductive_final_marking = inductive_miner.apply(
                        clu_list_log[clu_list.index(diff[j])])
                    fitness = replay_factory.apply(log, inductive_petri, inductive_initial_marking,
                                                   inductive_final_marking, variant="alignments")['averageFitness']
                    precision = precision_factory.apply(log, inductive_petri, inductive_initial_marking,
                                                        inductive_final_marking)
                    # fitness, precision = get_fit_prec_hpc(clu_list_log[clu_list.index(diff[j])],log)
                    F1 = 2 * fitness * precision / (fitness + precision)
                    # individual info for each sublog
                    length_li.append(length)
                    fit_li.append(fitness)
                    prec_li.append(precision)
                    F1_li.append(F1)

                # print("fit", fit_li)
                # print("prec", prec_li)
                if (i > 2):
                    del length_li[tempclu_list.index(diff_old[0])]
                    del fit_li[tempclu_list.index(diff_old[0])]
                    del prec_li[tempclu_list.index(diff_old[0])]
                    del F1_li[tempclu_list.index(diff_old[0])]
                del tempclu_list[tempclu_list.index(diff_old[0])]
            # print("del", tempclu_list)

            # print('length',length_li)
            print("fit", fit_li)
            print("prec", prec_li)
            print("F1", F1_li)

            plot_fit[str(i)] = np.average(fit_li)
            plot_prec[str(i)] = np.average(prec_li)
            plot_F1[str(i)] = np.average(F1_li)
            # plot_box[str(i)] = pd.Series(F1_li)
            plot_boxfit[str(i)] = fit_li[::]
            plot_boxprec[str(i)] = prec_li[::]
            plot_box[str(i)] = F1_li[::]
            # length_licopy = length_li[::]
            plot_length.append(length_li[::])
            print('plot_length', plot_length)
            print("plot_fit", plot_fit)
            print("plot_prec", plot_prec)
            print("plot_F1", plot_F1)

    print("plot_fit", plot_fit)
    print("plot_prec", plot_prec)
    print("plot_F1", plot_F1)
    print('length', plot_length)
    print('plot_box', plot_box)
    print('plot_boxfit', plot_boxfit)
    print('plot_boxprec', plot_boxprec)

    return plot_fit, plot_prec, plot_F1,plot_boxfit,plot_boxprec,plot_box,plot_length,runtime

def main_calc_leven(log, ATTR_NAME, METHOD, TYPE, PIC_PATH, percent, alpha,runtime,plot_clu):
    '''
    using levenshtein method without recomputing to get fitness, precision and F1-score of all cluster steps
    :param log:
    :param ATTR_NAME:
    :param METHOD:
    :param TYPE:
    :param percent:
    :param alpha:
    :param runtime:
    :param plot_clu:
    :return:
    '''
    list_of_vals = []
    list_log = []
    list_of_vals_dict = attributes_filter.get_trace_attribute_values(log, ATTR_NAME)

    list_of_vals_keys = list(list_of_vals_dict.keys())
    for i in range(len(list_of_vals_keys)):
        list_of_vals.append(list_of_vals_keys[i])

    print(list_of_vals)
    for i in range(len(list_of_vals)):
        logsample = log2sublog(log, list_of_vals[i], ATTR_NAME)
        list_log.append(logsample)
    print(len(list_log))

    # DFG test
    start = time.time()
    if METHOD == 'dfg':
        print("dfg is using!")
        y = evaluation.dfg_dis(list_log, percent, alpha)
    elif METHOD == 'DMM':
        print("DMM is using!")
        y = evaluation.eval_DMM_leven(list_log, percent, alpha)
    elif METHOD == 'avg':
        print("avg is using!")
        y = evaluation.eval_avg_leven(list_log, percent, alpha)
    # print(y)
    Z = linkage(y, method='average')
    # dist_mat = squareform(y)
    # Z = linkage_avg.linkage_dfg_update(list_log, dist_mat, alpha, percent)

    end = time.time()
    runtime[TYPE] = end - start
    # print(Z)
    print("runtime" + TYPE, runtime[TYPE])

    fig = plt.figure(figsize=(12, 10))
    dn = dendrogram(Z, labels=np.array(list_of_vals))
    # plt.title('Hierarchical Clustering Dendrogram')
    plt.xlabel(ATTR_NAME)
    plt.ylabel('Distance')
    plt.savefig(PIC_PATH + 'cluster_wupdate' + '_' + TYPE + '.svg')

    plot_fit = dict()
    plot_prec = dict()
    plot_F1 = dict()
    plot_box = dict()
    plot_box2 = dict()
    plot_boxfit = dict()
    plot_boxprec = dict()
    plot_length = []
    clu_list_dict = dict()
    length_li = []
    fit_li = []
    prec_li = []
    F1_li = []
    for i in range(1, plot_clu + 1):
        if i == 1:
            inductive_petri, inductive_initial_marking, inductive_final_marking = inductive_miner.apply(log)
            fitness = replay_factory.apply(log, inductive_petri, inductive_initial_marking,
                                           inductive_final_marking, variant="alignments")['averageFitness']

            precision = precision_factory.apply(log, inductive_petri, inductive_initial_marking,
                                                inductive_final_marking)
            # fitness, precision = get_fit_prec_hpc(log, log)
            F1 = 2 * fitness * precision / (fitness + precision)
            print("fit", fitness)
            print("prec", precision)
            plot_fit[str(i)] = fitness
            plot_prec[str(i)] = precision
            plot_F1[str(i)] = F1
            # plot_box[str(i)] = pd.Series(F1)
            plot_boxfit[str(i)] = fitness
            plot_boxprec[str(i)] = precision
            plot_box[str(i)] = F1
            plot_length.append([len(log)])
            tempclu_list_log = [list_log]
            tempclu_list = [list_of_vals]
        else:
            # print("tempclu_list",tempclu_list)
            clu_list_log, clu_list = clusteredlog(Z, i, list_of_vals, log, METHOD, ATTR_NAME)
            # length_li = []
            # fit_li = []
            # prec_li = []
            # F1_li = []
            # for j in range(0, i):
            #     length = len(clu_list_log[j])
            #     if length != 0:
            #         inductive_petri, inductive_initial_marking, inductive_final_marking = inductive_miner.apply(
            #             clu_list_log[j])
            #         fitness = replay_factory.apply(log, inductive_petri, inductive_initial_marking,
            #                                        inductive_final_marking, variant="alignments")['averageFitness']
            #         precision = precision_factory.apply(log, inductive_petri, inductive_initial_marking,
            #                                             inductive_final_marking)
            #         # fitness, precision = get_fit_prec_hpc(clu_list_log[j], log)
            #         F1 = 2 * fitness * precision / (fitness + precision)
            #         # individual info for each sublog
            #         length_li.append(length)
            #         fit_li.append(fitness)
            #         prec_li.append(precision)
            #         F1_li.append(F1)

            if len(clu_list_log[-1])!=0:
                # print("lenclu_list_log",len(clu_list_log))
                diff = [item for item in clu_list if not item in tempclu_list]
                diff_old = [item for item in tempclu_list if not item in clu_list]
                # print("diff",diff)
                # print("diff_old", diff_old)
                tempclu_list.append(clu_list[clu_list.index(diff[0])])
                tempclu_list.append(clu_list[clu_list.index(diff[1])])
                # print(tempclu_list)


                tempclu_list_log.append(clu_list_log[clu_list.index(diff[0])])
                tempclu_list_log.append(clu_list_log[clu_list.index(diff[1])])
                # print(len(tempclu_list_log))
                if (len(diff) > 2):
                    for k in range(0, len(diff) - 2):
                        tempclu_list.append(clu_list[clu_list.index(diff[2 + k])])
                        tempclu_list_log.append(clu_list_log[clu_list.index(diff[2 + k])])

                del tempclu_list_log[tempclu_list.index(diff_old[0])]
                # print("del",len(tempclu_list_log))
                # clu_list_dict[str(i)] = clu_list

                for j in range(0, len(diff)):
                    length = len(clu_list_log[clu_list.index(diff[j])])
                    inductive_petri, inductive_initial_marking, inductive_final_marking = inductive_miner.apply(
                        clu_list_log[clu_list.index(diff[j])])
                    fitness = replay_factory.apply(log, inductive_petri, inductive_initial_marking,
                                                   inductive_final_marking, variant="alignments")['averageFitness']
                    precision = precision_factory.apply(log, inductive_petri, inductive_initial_marking,
                                                        inductive_final_marking)
                    # fitness, precision = get_fit_prec_hpc(clu_list_log[clu_list.index(diff[j])],log)
                    F1 = 2 * fitness * precision / (fitness + precision)
                    # individual info for each sublog
                    length_li.append(length)
                    fit_li.append(fitness)
                    prec_li.append(precision)
                    F1_li.append(F1)

                # print("fit", fit_li)
                # print("prec", prec_li)
                if (i > 2):
                    del length_li[tempclu_list.index(diff_old[0])]
                    del fit_li[tempclu_list.index(diff_old[0])]
                    del prec_li[tempclu_list.index(diff_old[0])]
                    del F1_li[tempclu_list.index(diff_old[0])]
                del tempclu_list[tempclu_list.index(diff_old[0])]
            # print("del", tempclu_list)

            # print('length',length_li)
            print("fit", fit_li)
            print("prec", prec_li)
            print("F1", F1_li)

            plot_fit[str(i)] = np.average(fit_li)
            plot_prec[str(i)] = np.average(prec_li)
            plot_F1[str(i)] = np.average(F1_li)
            # plot_box[str(i)] = pd.Series(F1_li)
            plot_boxfit[str(i)] = fit_li[::]
            plot_boxprec[str(i)] = prec_li[::]
            plot_box[str(i)] = F1_li[::]
            # length_licopy = length_li[::]
            plot_length.append(length_li[::])
            print('plot_length', plot_length)
            print("plot_fit", plot_fit)
            print("plot_prec", plot_prec)
            print("plot_F1", plot_F1)

    print("plot_fit", plot_fit)
    print("plot_prec", plot_prec)
    print("plot_F1", plot_F1)
    print('length', plot_length)
    print('plot_box', plot_box)
    print('plot_boxfit', plot_boxfit)
    print('plot_boxprec', plot_boxprec)

    return plot_fit, plot_prec, plot_F1,plot_boxfit,plot_boxprec,plot_box,plot_length,runtime

def main_calc(log, ATTR_NAME, METHOD, TYPE, PIC_PATH, percent, alpha,runtime,plot_clu):
    '''
    using feature vector method without recomputing to get fitness, precision and F1-score of all cluster steps
    :param log:
    :param ATTR_NAME:
    :param METHOD:
    :param TYPE:
    :param percent:
    :param alpha:
    :param runtime:
    :param plot_clu:
    :return:
    '''
    list_of_vals = []
    list_log = []
    list_of_vals_dict = attributes_filter.get_trace_attribute_values(log, ATTR_NAME)

    list_of_vals_keys = list(list_of_vals_dict.keys())
    for i in range(len(list_of_vals_keys)):
        list_of_vals.append(list_of_vals_keys[i])

    print(list_of_vals)
    for i in range(len(list_of_vals)):
        logsample = log2sublog(log, list_of_vals[i], ATTR_NAME)
        list_log.append(logsample)
    print(len(list_log))

    # DFG test
    start = time.time()
    if METHOD == 'dfg':
        print("dfg is using!")
        y = evaluation.dfg_dis(list_log, percent, alpha)
    elif METHOD == 'DMM':
        print("DMM is using!")
        y = evaluation.eval_DMM_variant(list_log, percent, alpha)
    elif METHOD == 'avg':
        print("avg is using!")
        y = evaluation.eval_avg_variant(list_log, percent, alpha)
    # print(y)
    Z = linkage(y, method='average')
    # dist_mat = squareform(y)
    # Z = linkage_avg.linkage_dfg_update(list_log, dist_mat, alpha, percent)

    end = time.time()
    runtime[TYPE] = end - start
    # print(Z)
    print("runtime" + TYPE, runtime[TYPE])

    fig = plt.figure(figsize=(12, 10))
    dn = dendrogram(Z, labels=np.array(list_of_vals))
    # plt.title('Hierarchical Clustering Dendrogram')
    plt.xlabel(ATTR_NAME)
    plt.ylabel('Distance')
    plt.savefig(PIC_PATH + 'cluster_wupdate' + '_' + TYPE + '.svg')

    clu_index = fcluster(Z, 3, criterion='maxclust')
    clu_index = dict(zip(list_of_vals, clu_index))
    print('clu_index', clu_index)

    plot_fit = dict()
    plot_prec = dict()
    plot_F1 = dict()
    plot_box = dict()
    plot_box2 = dict()
    plot_boxfit = dict()
    plot_boxprec = dict()
    plot_length = []
    clu_list_dict = dict()
    length_li = []
    fit_li = []
    prec_li = []
    F1_li = []
    for i in range(1, plot_clu + 1):
        if i == 1:
            inductive_petri, inductive_initial_marking, inductive_final_marking = inductive_miner.apply(log)
            fitness = replay_factory.apply(log, inductive_petri, inductive_initial_marking,
                                           inductive_final_marking, variant="alignments")['averageFitness']

            precision = precision_factory.apply(log, inductive_petri, inductive_initial_marking,
                                                inductive_final_marking)
            # fitness, precision = get_fit_prec_hpc(log, log)
            F1 = 2 * fitness * precision / (fitness + precision)
            print("fit", fitness)
            print("prec", precision)
            plot_fit[str(i)] = fitness
            plot_prec[str(i)] = precision
            plot_F1[str(i)] = F1
            # plot_box[str(i)] = pd.Series(F1)
            plot_boxfit[str(i)] = fitness
            plot_boxprec[str(i)] = precision
            plot_box[str(i)] = F1
            plot_length.append([len(log)])
            tempclu_list_log = [list_log]
            tempclu_list = [list_of_vals]
        else:
            # print("tempclu_list",tempclu_list)
            clu_list_log, clu_list = clusteredlog(Z, i, list_of_vals, log, METHOD, ATTR_NAME)
            # length_li = []
            # fit_li = []
            # prec_li = []
            # F1_li = []
            # for j in range(0, i):
            #     length = len(clu_list_log[j])
            #     if length != 0:
            #         # inductive_petri, inductive_initial_marking, inductive_final_marking = inductive_miner.apply(
            #         #     clu_list_log[j])
            #         # fitness = replay_factory.apply(log, inductive_petri, inductive_initial_marking,
            #         #                                inductive_final_marking, variant="alignments")['averageFitness']
            #         # precision = precision_factory.apply(log, inductive_petri, inductive_initial_marking,
            #         #                                     inductive_final_marking)
            #         fitness, precision = get_fit_prec_hpc(clu_list_log[j], log)
            #         F1 = 2 * fitness * precision / (fitness + precision)
            #         # individual info for each sublog
            #         length_li.append(length)
            #         fit_li.append(fitness)
            #         prec_li.append(precision)
            #         F1_li.append(F1)

            if len(clu_list_log[-1]) != 0:
                # print("lenclu_list_log",len(clu_list_log))
                diff = [item for item in clu_list if not item in tempclu_list]
                diff_old = [item for item in tempclu_list if not item in clu_list]
                # print("diff",diff)
                # print("diff_old", diff_old)
                tempclu_list.append(clu_list[clu_list.index(diff[0])])
                tempclu_list.append(clu_list[clu_list.index(diff[1])])
                # print(tempclu_list)

                tempclu_list_log.append(clu_list_log[clu_list.index(diff[0])])
                tempclu_list_log.append(clu_list_log[clu_list.index(diff[1])])
                # print(len(tempclu_list_log))
                if (len(diff) > 2):
                    for k in range(0, len(diff) - 2):
                        tempclu_list.append(clu_list[clu_list.index(diff[2 + k])])
                        tempclu_list_log.append(clu_list_log[clu_list.index(diff[2 + k])])

                del tempclu_list_log[tempclu_list.index(diff_old[0])]
                # print("del",len(tempclu_list_log))
                # clu_list_dict[str(i)] = clu_list

                for j in range(0, len(diff)):
                    length = len(clu_list_log[clu_list.index(diff[j])])
                    inductive_petri, inductive_initial_marking, inductive_final_marking = inductive_miner.apply(
                        clu_list_log[clu_list.index(diff[j])])
                    fitness = replay_factory.apply(log, inductive_petri, inductive_initial_marking,
                                                   inductive_final_marking, variant="alignments")['averageFitness']
                    precision = precision_factory.apply(log, inductive_petri, inductive_initial_marking,
                                                        inductive_final_marking)
                    # fitness, precision = get_fit_prec_hpc(clu_list_log[clu_list.index(diff[j])],log)
                    F1 = 2 * fitness * precision / (fitness + precision)
                    # individual info for each sublog
                    length_li.append(length)
                    fit_li.append(fitness)
                    prec_li.append(precision)
                    F1_li.append(F1)

                # print("fit", fit_li)
                # print("prec", prec_li)
                if (i > 2):
                    del length_li[tempclu_list.index(diff_old[0])]
                    del fit_li[tempclu_list.index(diff_old[0])]
                    del prec_li[tempclu_list.index(diff_old[0])]
                    del F1_li[tempclu_list.index(diff_old[0])]
                del tempclu_list[tempclu_list.index(diff_old[0])]
            # print("del", tempclu_list)

            # print('length',length_li)
            print("fit", fit_li)
            print("prec", prec_li)
            print("F1", F1_li)

            plot_fit[str(i)] = np.average(fit_li)
            plot_prec[str(i)] = np.average(prec_li)
            plot_F1[str(i)] = np.average(F1_li)
            # plot_box[str(i)] = pd.Series(F1_li)
            plot_boxfit[str(i)] = fit_li[::]
            plot_boxprec[str(i)] = prec_li[::]
            plot_box[str(i)] = F1_li[::]
            # length_licopy = length_li[::]
            plot_length.append(length_li[::])
            print('plot_length', plot_length)
            print("plot_fit", plot_fit)
            print("plot_prec", plot_prec)
            print("plot_F1", plot_F1)

    print("plot_fit", plot_fit)
    print("plot_prec", plot_prec)
    print("plot_F1", plot_F1)
    print('length', plot_length)
    print('plot_box', plot_box)
    print('plot_boxfit', plot_boxfit)
    print('plot_boxprec', plot_boxprec)

    return plot_fit, plot_prec, plot_F1,plot_boxfit,plot_boxprec,plot_box,plot_length,runtime


def five_plots(plot_fit, plot_prec, plot_F1,plot_boxfit,plot_boxprec,plot_box,plot_length,plot_clu,x_axis,PIC_PATH,TYPE):
    '''
    generate five plots w.r.t number of cluster, i.e., fitness, precision, F1-score and cluster size
    :param plot_fit:
    :param plot_prec:
    :param plot_F1:
    :param plot_boxfit:
    :param plot_boxprec:
    :param plot_box:
    :param plot_length:
    :param plot_clu:
    :param x_axis:
    :param PIC_PATH:
    :param TYPE:
    :return:
    '''
    for i in range(1, plot_clu + 1):
        plot_box[str(i)] = pd.Series(plot_box[str(i)])
        plot_boxfit[str(i)] = pd.Series(plot_boxfit[str(i)])
        plot_boxprec[str(i)] = pd.Series(plot_boxprec[str(i)])
    fig = plt.figure()
    # rc('text', usetex=True)
    # rc('font', family='serif')
    data = pd.DataFrame(plot_boxfit)
    # print(data)
    plt.plot(x_axis, list(plot_fit.values()), color="b", linestyle="-", marker="s", linewidth=1)
    plt.hlines(list(plot_fit.values())[0], 1, plot_clu, colors="b", linestyles="dashed")
    plt.xticks(x_axis)
    data.boxplot(sym='o', whis=1)
    # plt.gca().invert_xaxis()
    # plt.ylim(np.min(list(plot_F1.values()))-0.01,1)
    plt.ylim(0, 1.04)
    plt.xlabel("Num. of Cluster")
    plt.ylabel("Fitness")
    plt.grid(axis='x')
    plt.savefig(PIC_PATH + 'fit_sca' + '_' + TYPE + '.svg')

    fig2 = plt.figure()
    # rc('text', usetex=True)
    # rc('font', family='serif')
    data = pd.DataFrame(plot_boxprec)
    # print(data)
    plt.plot(x_axis, list(plot_prec.values()), color="b", linestyle="-", marker="s", linewidth=1)
    plt.hlines(list(plot_prec.values())[0], 1, plot_clu, colors="b", linestyles="dashed")
    plt.xticks(x_axis)
    data.boxplot(sym='o', whis=1)
    # plt.gca().invert_xaxis()
    # plt.ylim(np.min(list(plot_F1.values()))-0.01,1)
    plt.ylim(0, 1.04)
    plt.xlabel("Num. of Cluster")
    plt.ylabel("Precision")
    plt.grid(axis='x')
    plt.savefig(PIC_PATH + 'prec_sca' + '_' + TYPE + '.svg')


    # rescale to 0-1
    fig4 = plt.figure()
    # plot_box["2"] = plot_box["1"]
    data = pd.DataFrame(plot_box)
    # print(data)
    # rc('text', usetex=True)
    # rc('font', family='serif')
    plt.plot(x_axis, list(plot_F1.values()), color="b", linestyle="-", marker="s", linewidth=1)
    plt.hlines(list(plot_F1.values())[0], 1, plot_clu, colors="b", linestyles="dashed")
    plt.xticks(x_axis)
    data.boxplot(sym='o', whis=1)

    plt.ylim(0, 1.04)
    # plt.gca().invert_xaxis()
    plt.xlabel("Num. of Cluster")
    plt.ylabel("F1-Score")
    plt.grid(axis='x')
    plt.savefig(PIC_PATH + 'f1_boxplot_sca' + '_' + TYPE + '.svg')
    #
    # show cluster size dot
    fig6 = plt.figure()
    # rc('text', usetex=True)
    # rc('font', family='serif')
    for i in range(0, plot_clu):
        xlist = np.ones(len(plot_length[i])) * (i + 1)
        a = sorted(dict(Counter(plot_length[i])).items(), key=lambda x: x[0])
        weights = [20 * a[j][1] for j in range(len(a)) for k in range(a[j][1])]
        plot_length[i] = sorted(plot_length[i], reverse=False)
        plt.scatter(xlist, plot_length[i], marker="o", s=weights)
    plt.xticks(range(1, plot_clu+1))
    plt.ylim(np.min(np.min(plot_length))/2, np.max(np.max(plot_length))+500)
    plt.yscale('log')
    plt.xlabel("Num. of Cluster")
    plt.ylabel("Cluster Size")
    plt.grid(axis='y')
    plt.savefig(PIC_PATH + 'dot_clustersize' + '_' + TYPE + '.svg')
