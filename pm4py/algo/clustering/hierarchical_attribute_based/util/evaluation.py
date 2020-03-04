from scipy.spatial.distance import squareform
import numpy as np
from pm4py.algo.clustering.hierarchical_attribute_based.variant import act_dist_calc
from pm4py.algo.clustering.hierarchical_attribute_based.variant import suc_dist_calc
from pm4py.algo.clustering.hierarchical_attribute_based.leven_dist import leven_dist_calc
from pm4py.algo.clustering.hierarchical_attribute_based.dfg import dfg_dist


def dfg_dis(loglist, percent, alpha):
    size = len(loglist)
    # print(size)
    dist_mat = np.zeros((size, size))

    for i in range(0, size - 1):
        for j in range(i + 1, size):
            (dist_act, dist_dfg) = dfg_dist.dfg_dist_calc(loglist[i], loglist[j])
            # print([i, j, dist_act, dist_dfg])
            if(j%50==0):
                print([i, j, dist_act, dist_dfg])
            dist_mat[i][j] = dist_act * alpha + dist_dfg * (1 - alpha)
            dist_mat[j][i] = dist_mat[i][j]

    # print(dist_mat)

    y = squareform(dist_mat)
    # print(y)
    # Z = linkage(y, method='average')
    # print(Z)
    # print(cophenet(Z, y))  # return vector is the pairwise dist generated from Z
    # fig = plt.figure(figsize=(10, 8))
    # # dn = fancy_dendrogram(Z, max_d=0.35)
    # # dn = dendrogram(Z)
    # dn = dendrogram(Z,labels=np.array(list_of_vals))
    # # plt.title('Hierarchical Clustering Dendrogram')
    # plt.xlabel('Credit Score')
    # plt.ylabel('Distance')
    # plt.savefig('cluster.svg')
    # plt.show()
    return y


def eval_avg_variant(loglist, percent, alpha):

    size = len(loglist)
    #print(size)
    dist_mat = np.zeros((size, size))

    for i in range(0, size - 1):
        for j in range(i + 1, size):
            dist_act = act_dist_calc.act_sim_percent_avg(loglist[i], loglist[j],percent,percent)
            dist_suc = suc_dist_calc.suc_sim_percent_avg(loglist[i], loglist[j], percent, percent)
            if (j % 50 == 0):
                print([i,j,dist_act,dist_suc])
            dist_mat[i][j] = dist_act * alpha + dist_suc * (1 - alpha)
            dist_mat[j][i] = dist_mat[i][j]

    # print(dist_mat)

    y = squareform(dist_mat)
    # print(y)
    # Z = linkage(y, method='average')
    # print(Z)
    # print(cophenet(Z, y))  # return vector is the pairwise dist generated from Z
    # plt.figure(figsize=(10, 8))
    # # dn = fancy_dendrogram(Z, max_d=0.35)
    # dn = dendrogram(Z)
    # # dn = dendrogram(Z,labels=np.array(list_of_vals))
    # # plt.title('Hierarchical Clustering Dendrogram')
    # plt.xlabel('Case Index')
    # plt.ylabel('Distance')
    # plt.savefig('cluster.svg')
    # plt.show()

    return y


def eval_DMM_variant(loglist, percent, alpha):

    size = len(loglist)
    #print(size)
    dist_mat = np.zeros((size, size))
    # print("stop1")

    for i in range(0, size - 1):
        for j in range(i + 1, size):
            # print("stop2")
            dist_act = act_dist_calc.act_sim_percent(loglist[i], loglist[j],percent,percent)
            # print("stop3")
            dist_suc = suc_dist_calc.suc_sim_percent(loglist[i], loglist[j], percent, percent)
            if (j % 50 == 0):
                print([i, j, dist_act, dist_suc])
            dist_mat[i][j] = dist_act * alpha + dist_suc * (1 - alpha)
            dist_mat[j][i] = dist_mat[i][j]

    # print(dist_mat)

    y = squareform(dist_mat)
    # print(y)
    # Z = linkage(y, method='average')
    # print(Z)
    # print(cophenet(Z, y))  # return vector is the pairwise dist generated from Z
    # plt.figure(figsize=(10, 8))
    # # dn = fancy_dendrogram(Z, max_d=0.35)
    # dn = dendrogram(Z)
    # # dn = dendrogram(Z,labels=np.array(list_of_vals))
    # # plt.title('Hierarchical Clustering Dendrogram')
    # plt.xlabel('Case Index')
    # plt.ylabel('Distance')
    # plt.savefig('cluster.svg')
    # plt.show()
    return y

def eval_avg_leven(loglist, percent, alpha):

    size = len(loglist)
    #print(size)
    dist_mat = np.zeros((size, size))

    for i in range(0, size - 1):
        for j in range(i + 1, size):
            dist_mat[i][j] = leven_dist_calc.leven_dist_avg(loglist[i], loglist[j], percent, percent)
            if (j % 50 == 0):
                print([i, j, dist_mat[i][j]])
            dist_mat[j][i] = dist_mat[i][j]

    # print(dist_mat)

    y = squareform(dist_mat)
    # print(y)
    # Z = linkage(y, method='average')
    # print(Z)
    # print(cophenet(Z, y))  # return vector is the pairwise dist generated from Z
    # plt.figure(figsize=(10, 8))
    # # dn = fancy_dendrogram(Z, max_d=0.35)
    # dn = dendrogram(Z)
    # # dn = dendrogram(Z,labels=np.array(list_of_vals))
    # plt.title('Hierarchical Clustering Dendrogram')
    # #plt.xlabel('Loan Amount')
    # plt.ylabel('Distance')
    # plt.savefig('cluster.svg')
    # plt.show()
    return y

def eval_DMM_leven(loglist, percent, alpha):

    size = len(loglist)
    #print(size)
    dist_mat = np.zeros((size, size))

    for i in range(0, size - 1):
        for j in range(i + 1, size):
            dist_mat[i][j] = leven_dist_calc.leven_dist(loglist[i], loglist[j], percent, percent)
            if (j % 50 == 0):
                print([i, j, dist_mat[i][j]])
            dist_mat[j][i] = dist_mat[i][j]

    # print(dist_mat)

    y = squareform(dist_mat)
    print(y)
    return y


