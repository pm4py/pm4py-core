'''
    This file is part of PM4Py (More Info: https://pm4py.fit.fraunhofer.de).

    PM4Py is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    PM4Py is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with PM4Py.  If not, see <https://www.gnu.org/licenses/>.
'''
import numpy as np
from scipy.spatial.distance import squareform
from pm4py.algo.clustering.trace_attribute_driven.leven_dist import leven_dist_calc
from pm4py.algo.clustering.trace_attribute_driven.merge_log import merge_log
from pm4py.algo.clustering.trace_attribute_driven.dfg import dfg_dist
from pm4py.algo.clustering.trace_attribute_driven.variants import act_dist_calc
from pm4py.algo.clustering.trace_attribute_driven.variants import suc_dist_calc


def linkage_dfg_update(loglist, dist_mat, alpha, percent):
    index_list = []
    for i in range(len(dist_mat)):
        for j in range(i + 1, len(dist_mat)):
            index_list.append([i, j])

    y = squareform(dist_mat)
    n = len(dist_mat)  # The number of observations.
    Z = []
    cluster_size = dict(zip(range(n), np.ones(n)))  # record merged cluster size every step
    k = 1
    logsindex = list(range(len(loglist)))
    while (k <= n - 2):
        min_index = np.argmin(y)

        # update Z
        temp = []
        temp.extend(index_list[min_index])
        temp.append(y[min_index])
        cluster_size[n - 1 + k] = cluster_size[temp[0]] + cluster_size[temp[1]]
        temp.append(cluster_size[n - 1 + k])

        Z.append(temp)

        # get index of min in y
        item = index_list[min_index][::]
        record1 = []
        record2 = []
        for ele in index_list:
            if item[0] in ele:
                record1.append(index_list.index(ele))
                inde = ele.index(item[0])
                ele[inde] = n - 1 + k
            if item[1] in ele:  # here if/elif both works
                record2.append(index_list.index(ele))
                inde = ele.index(item[1])
                ele[inde] = n - 1 + k
            ele.sort()

        record = list(set(record1).union(set(record2)))

        merged1 = merge_log.update_merge([loglist[item[0]], loglist[item[1]]])
        # here the logsindex is changing
        diff = list(set(logsindex).difference(set(item)))  # diff is the node number need to be updated

        update_dist = dict()
        for ele in diff:
            (dist_act, dist_dfg) = dfg_dist.dfg_dist_calc(merged1, loglist[ele])
            tempdist = dist_act * alpha + dist_dfg * (1 - alpha)
            # tempdist = leven_dist_calc.leven_dist_avg(merged1, loglist[ele], percent, percent)
            update_dist[ele] = tempdist

        loglist.append(merged1)
        diff.append(n - 1 + k)
        logsindex = diff

        del (record1[record1.index(min_index)])
        del (record2[record2.index(min_index)])

        # for i in range(len(record1)):
        #     y[record1[i]] = (y[record1[i]]*cluster_size[item[0]] + y[record2[i]]*cluster_size[item[1]]) / (cluster_size[item[0]]+cluster_size[item[1]])
        for ele in record1:
            uindex = index_list[ele][0]  # record1 is the location if nodes in diff in the index_list
            y[ele] = update_dist[uindex]

        diff1 = list(set(range(len(index_list))).difference(set(record)))
        newindex = record1 + diff1
        newindex.sort()

        range_newindex = range(len(newindex))
        tempy = list(range_newindex)
        templist = list(range_newindex)
        for i in range_newindex:
            tempy[i] = y[newindex[i]]
            templist[i] = index_list[newindex[i]]

        index_list = templist
        y = tempy
        k = k + 1

    temp = []
    temp.extend(index_list[0])
    temp.append(y[0])

    cluster_size[n - 1 + k] = cluster_size[temp[0]] + cluster_size[temp[1]]
    temp.append(cluster_size[n - 1 + k])
    Z.append(temp)
    Z = np.array(Z)

    return Z


def linkage_avg(loglist, dist_mat, alpha, percent):
    index_list = []
    cluster_size = []
    for i in range(len(dist_mat)):
        cluster_size.append(len(loglist[i]))
        for j in range(i + 1, len(dist_mat)):
            index_list.append([i, j])

    y = squareform(dist_mat)
    n = len(dist_mat)  # The number of observations.
    Z = []
    cluster_size = dict(zip(range(n), cluster_size))  # record merged cluster size every step
    k = 1
    while (k <= n - 2):
        min_index = np.argmin(y)

        # update Z
        temp = []
        temp.extend(index_list[min_index])
        temp.append(y[min_index])
        cluster_size[n - 1 + k] = cluster_size[temp[0]] + cluster_size[temp[1]]
        temp.append(cluster_size[n - 1 + k])

        Z.append(temp)

        # get index of min in y
        item = index_list[min_index][::]
        record1 = []
        record2 = []
        for ele in index_list:
            if item[0] in ele:
                record1.append(index_list.index(ele))
                inde = ele.index(item[0])
                ele[inde] = n - 1 + k
            if item[1] in ele:  # here if/elif both works
                record2.append(index_list.index(ele))
                inde = ele.index(item[1])
                ele[inde] = n - 1 + k
            ele.sort()

        record = list(set(record1).union(set(record2)))

        del (record1[record1.index(min_index)])
        del (record2[record2.index(min_index)])

        for i in range(len(record1)):
            y[record1[i]] = (y[record1[i]] * cluster_size[item[0]] + y[record2[i]] * cluster_size[item[1]]) / (
                        cluster_size[item[0]] + cluster_size[item[1]])
        # for ele in record1:
        #     uindex = index_list[ele][0]  # record1 is the location if nodes in diff in the index_list
        #     y[ele] = update_dist[uindex]

        diff1 = list(set(range(len(index_list))).difference(set(record)))
        newindex = record1 + diff1
        newindex.sort()

        range_newindex = range(len(newindex))
        tempy = list(range_newindex)
        templist = list(range_newindex)
        for i in range_newindex:
            tempy[i] = y[newindex[i]]
            templist[i] = index_list[newindex[i]]

        index_list = templist
        y = tempy
        k = k + 1

    temp = []
    temp.extend(index_list[0])
    temp.append(y[0])

    cluster_size[n - 1 + k] = cluster_size[temp[0]] + cluster_size[temp[1]]
    temp.append(cluster_size[n - 1 + k])
    Z.append(temp)
    Z = np.array(Z)

    return Z


def linkage_DMM_update(loglist, dist_mat, alpha, percent):
    index_list = []
    for i in range(len(dist_mat)):
        for j in range(i + 1, len(dist_mat)):
            index_list.append([i, j])

    y = squareform(dist_mat)
    n = len(dist_mat)  # The number of observations.
    Z = []
    cluster_size = dict(zip(range(n), np.ones(n)))  # record merged cluster size every step
    k = 1
    logsindex = list(range(len(loglist)))
    while (k <= n - 2):
        min_index = np.argmin(y)

        # update Z
        temp = []
        temp.extend(index_list[min_index])
        temp.append(y[min_index])
        cluster_size[n - 1 + k] = cluster_size[temp[0]] + cluster_size[temp[1]]
        temp.append(cluster_size[n - 1 + k])

        Z.append(temp)

        # get index of min in y
        item = index_list[min_index][::]
        record1 = []
        record2 = []
        for ele in index_list:
            if item[0] in ele:
                record1.append(index_list.index(ele))
                inde = ele.index(item[0])
                ele[inde] = n - 1 + k
            if item[1] in ele:  # here if/elif both works
                record2.append(index_list.index(ele))
                inde = ele.index(item[1])
                ele[inde] = n - 1 + k
            ele.sort()

        record = list(set(record1).union(set(record2)))

        merged1 = merge_log.update_merge([loglist[item[0]], loglist[item[1]]])
        # here the logsindex is changing
        diff = list(set(logsindex).difference(set(item)))  # diff is the node number need to be updated

        update_dist = dict()
        for ele in diff:
            dist_act = act_dist_calc.act_sim_percent(merged1, loglist[ele], percent, percent)
            dist_suc = suc_dist_calc.suc_sim_percent(merged1, loglist[ele], percent, percent)
            tempdist = dist_act * alpha + dist_suc * (1 - alpha)
            # tempdist = leven_dist_calc.leven_dist_avg(merged1, loglist[ele], percent, percent)
            update_dist[ele] = tempdist

        loglist.append(merged1)
        diff.append(n - 1 + k)
        logsindex = diff

        del (record1[record1.index(min_index)])
        del (record2[record2.index(min_index)])

        # for i in range(len(record1)):
        #     y[record1[i]] = (y[record1[i]]*cluster_size[item[0]] + y[record2[i]]*cluster_size[item[1]]) / (cluster_size[item[0]]+cluster_size[item[1]])
        for ele in record1:
            uindex = index_list[ele][0]  # record1 is the location if nodes in diff in the index_list
            y[ele] = update_dist[uindex]

        diff1 = list(set(range(len(index_list))).difference(set(record)))
        newindex = record1 + diff1
        newindex.sort()

        range_newindex = range(len(newindex))
        tempy = list(range_newindex)
        templist = list(range_newindex)
        for i in range_newindex:
            tempy[i] = y[newindex[i]]
            templist[i] = index_list[newindex[i]]

        index_list = templist
        y = tempy
        k = k + 1

    temp = []
    temp.extend(index_list[0])
    temp.append(y[0])

    cluster_size[n - 1 + k] = cluster_size[temp[0]] + cluster_size[temp[1]]
    temp.append(cluster_size[n - 1 + k])
    Z.append(temp)
    Z = np.array(Z)

    return Z


def linkage_DMM_update_leven(loglist, dist_mat, alpha, percent):
    index_list = []
    for i in range(len(dist_mat)):
        for j in range(i + 1, len(dist_mat)):
            index_list.append([i, j])

    y = squareform(dist_mat)
    n = len(dist_mat)  # The number of observations.
    Z = []
    cluster_size = dict(zip(range(n), np.ones(n)))  # record merged cluster size every step
    k = 1
    logsindex = list(range(len(loglist)))
    while (k <= n - 2):
        min_index = np.argmin(y)

        # update Z
        temp = []
        temp.extend(index_list[min_index])
        temp.append(y[min_index])
        cluster_size[n - 1 + k] = cluster_size[temp[0]] + cluster_size[temp[1]]
        temp.append(cluster_size[n - 1 + k])

        Z.append(temp)

        # get index of min in y
        item = index_list[min_index][::]
        record1 = []
        record2 = []
        for ele in index_list:
            if item[0] in ele:
                record1.append(index_list.index(ele))
                inde = ele.index(item[0])
                ele[inde] = n - 1 + k
            if item[1] in ele:  # here if/elif both works
                record2.append(index_list.index(ele))
                inde = ele.index(item[1])
                ele[inde] = n - 1 + k
            ele.sort()

        record = list(set(record1).union(set(record2)))

        merged1 = merge_log.update_merge([loglist[item[0]], loglist[item[1]]])
        # here the logsindex is changing
        diff = list(set(logsindex).difference(set(item)))  # diff is the node number need to be updated

        update_dist = dict()
        for ele in diff:
            tempdist = leven_dist_calc.leven_dist(merged1, loglist[ele], percent, percent)
            # tempdist = leven_dist_calc.leven_dist_avg(merged1, loglist[ele], percent, percent)
            update_dist[ele] = tempdist

        loglist.append(merged1)
        diff.append(n - 1 + k)
        logsindex = diff

        del (record1[record1.index(min_index)])
        del (record2[record2.index(min_index)])

        # for i in range(len(record1)):
        #     y[record1[i]] = (y[record1[i]]*cluster_size[item[0]] + y[record2[i]]*cluster_size[item[1]]) / (cluster_size[item[0]]+cluster_size[item[1]])
        for ele in record1:
            uindex = index_list[ele][0]  # record1 is the location if nodes in diff in the index_list
            y[ele] = update_dist[uindex]

        diff1 = list(set(range(len(index_list))).difference(set(record)))
        newindex = record1 + diff1
        newindex.sort()

        range_newindex = range(len(newindex))
        tempy = list(range_newindex)
        templist = list(range_newindex)
        for i in range_newindex:
            tempy[i] = y[newindex[i]]
            templist[i] = index_list[newindex[i]]

        index_list = templist
        y = tempy
        k = k + 1

    temp = []
    temp.extend(index_list[0])
    temp.append(y[0])

    cluster_size[n - 1 + k] = cluster_size[temp[0]] + cluster_size[temp[1]]
    temp.append(cluster_size[n - 1 + k])
    Z.append(temp)
    Z = np.array(Z)

    return Z
