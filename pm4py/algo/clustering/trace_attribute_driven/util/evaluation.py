from scipy.spatial.distance import squareform
import numpy as np
from pm4py.algo.clustering.trace_attribute_driven.variant import act_dist_calc
from pm4py.algo.clustering.trace_attribute_driven.variant import suc_dist_calc
from pm4py.algo.clustering.trace_attribute_driven.leven_dist import leven_dist_calc
from pm4py.algo.clustering.trace_attribute_driven.dfg import dfg_dist


def dfg_dis(loglist, percent, alpha):
    size = len(loglist)
    dist_mat = np.zeros((size, size))

    for i in range(0, size - 1):
        for j in range(i + 1, size):
            (dist_act, dist_dfg) = dfg_dist.dfg_dist_calc(loglist[i], loglist[j])
            dist_mat[i][j] = dist_act * alpha + dist_dfg * (1 - alpha)
            dist_mat[j][i] = dist_mat[i][j]
    y = squareform(dist_mat)
    return y


def eval_avg_variant(loglist, percent, alpha):
    size = len(loglist)
    dist_mat = np.zeros((size, size))

    for i in range(0, size - 1):
        for j in range(i + 1, size):
            dist_act = act_dist_calc.act_sim_percent_avg(loglist[i], loglist[j], percent, percent)
            dist_suc = suc_dist_calc.suc_sim_percent_avg(loglist[i], loglist[j], percent, percent)
            dist_mat[i][j] = dist_act * alpha + dist_suc * (1 - alpha)
            dist_mat[j][i] = dist_mat[i][j]
    y = squareform(dist_mat)

    return y


def eval_DMM_variant(loglist, percent, alpha):
    size = len(loglist)
    dist_mat = np.zeros((size, size))

    for i in range(0, size - 1):
        for j in range(i + 1, size):
            dist_act = act_dist_calc.act_sim_percent(loglist[i], loglist[j], percent, percent)
            dist_suc = suc_dist_calc.suc_sim_percent(loglist[i], loglist[j], percent, percent)
            dist_mat[i][j] = dist_act * alpha + dist_suc * (1 - alpha)
            dist_mat[j][i] = dist_mat[i][j]
    y = squareform(dist_mat)
    return y


def eval_avg_leven(loglist, percent, alpha):
    size = len(loglist)
    dist_mat = np.zeros((size, size))

    for i in range(0, size - 1):
        for j in range(i + 1, size):
            dist_mat[i][j] = leven_dist_calc.leven_dist_avg(loglist[i], loglist[j], percent, percent)
            dist_mat[j][i] = dist_mat[i][j]
    y = squareform(dist_mat)
    return y


def eval_DMM_leven(loglist, percent, alpha):
    size = len(loglist)
    dist_mat = np.zeros((size, size))

    for i in range(0, size - 1):
        for j in range(i + 1, size):
            dist_mat[i][j] = leven_dist_calc.leven_dist(loglist[i], loglist[j], percent, percent)
            dist_mat[j][i] = dist_mat[i][j]
    y = squareform(dist_mat)
    return y
