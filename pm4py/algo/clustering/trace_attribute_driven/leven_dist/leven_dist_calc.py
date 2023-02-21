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
from pm4py.algo.clustering.trace_attribute_driven.util import filter_subsets
from pm4py.util import string_distance
import string


def leven_preprocess(list1, list2):
    '''
    this function transform event name to alphabet for the sake of levenshtein distance
    :param list1:
    :param list2:
    :return:
    '''

    listsum = sorted(list(set(list1 + list2)))
    alphabet = list(string.ascii_letters)[0:len(listsum)]
    str1 = [alphabet[listsum.index(item)] for item in list1]
    str2 = [alphabet[listsum.index(item)] for item in list2]
    str1 = ''.join(str1)
    str2 = ''.join(str2)
    return str1, str2


def leven_dist(log1, log2, percent_1, percent_2):
    '''

    this function compare the levenstein distance between two sublogs via the two lists of variants.
    '''

    (dataframe_1, var_list_1) = filter_subsets.sublog_percent(log1, percent_1)
    (dataframe_2, var_list_2) = filter_subsets.sublog_percent(log2, percent_2)

    if len(var_list_1) >= len(var_list_2):
        max_len = len(var_list_1)
        min_len = len(var_list_2)
        max_var = var_list_1
        min_var = var_list_2
        var_count_max = dataframe_1['count']
        var_count_min = dataframe_2['count']
    else:
        max_len = len(var_list_2)
        min_len = len(var_list_1)
        max_var = var_list_2
        min_var = var_list_1
        var_count_max = dataframe_2['count']
        var_count_min = dataframe_1['count']

    dist_matrix = np.zeros((max_len, min_len))
    max_per_var = np.zeros(max_len)
    max_freq = np.zeros(max_len)
    min_freq = np.zeros(min_len)
    min_per_var = np.zeros(min_len)
    index_rec = set(list(range(min_len)))

    if var_list_1 == var_list_2:
        dist = 0
    else:
        for i in range(max_len):
            dist_vec = np.zeros(min_len)
            for j in range(min_len):
                (str1, str2) = leven_preprocess(max_var[i], min_var[j])
                max_len = np.max([len(str1), len(str2)])
                dist_vec[j] = (string_distance.levenshtein(str1, str2)) / max_len
                dist_matrix[i][j] = dist_vec[j]
                if j == (min_len - 1):
                    # max_loc_col = np.argmax(dist_matrix[i, :])  # location of max value
                    max_loc_col = np.argmin(dist_vec)
                    if abs(dist_vec[max_loc_col]) <= 1e-8:
                        index_rec.discard(max_loc_col)
                        max_freq[i] = var_count_max.iloc[i] * var_count_min.iloc[max_loc_col] * 2
                        max_per_var[i] = dist_vec[max_loc_col] * max_freq[i] * 2
                    else:
                        max_freq[i] = var_count_max.iloc[i] * var_count_min.iloc[max_loc_col]
                        max_per_var[i] = dist_vec[max_loc_col] * max_freq[i]

        if (len(index_rec) != 0):
            for i in list(index_rec):
                min_loc_row = np.argmin(dist_matrix[:, i])
                min_freq[i] = var_count_max.iloc[min_loc_row] * var_count_min.iloc[i]
                min_per_var[i] = dist_matrix[min_loc_row, i] * min_freq[i]

        dist = (np.sum(max_per_var) + np.sum(min_per_var)) / (np.sum(max_freq) + np.sum(min_freq))

    return dist


def leven_dist_avg(log1, log2, percent_1, percent_2):
    (dataframe_1, var_list_1) = filter_subsets.sublog_percent(log1, percent_1)
    (dataframe_2, var_list_2) = filter_subsets.sublog_percent(log2, percent_2)

    if len(var_list_1) >= len(var_list_2):
        max_len = len(var_list_1)
        min_len = len(var_list_2)
        max_var = var_list_1
        min_var = var_list_2
        var_count_max = dataframe_1['count']
        var_count_min = dataframe_2['count']
    else:
        max_len = len(var_list_2)
        min_len = len(var_list_1)
        max_var = var_list_2
        min_var = var_list_1
        var_count_max = dataframe_2['count']
        var_count_min = dataframe_1['count']

    dist_matrix = np.zeros((max_len, min_len))
    col_sum = np.zeros(max_len)

    for i in range(max_len):
        dist_vec = np.zeros(min_len)
        for j in range(min_len):
            (str1, str2) = leven_preprocess(max_var[i], min_var[j])
            max_len = np.max([len(str1), len(str2)])
            dist_vec[j] = (string_distance.levenshtein(str1, str2)) / max_len
            col_sum[i] += dist_vec[j] * var_count_max.iloc[i] * var_count_min.iloc[j]
            dist_matrix[i][j] = dist_vec[j]

    vmax_vec = (var_count_max.values).reshape(-1, 1)
    vmin_vec = (var_count_min.values).reshape(1, -1)
    vec_sum = np.sum(np.dot(vmax_vec, vmin_vec))
    dist = np.sum(col_sum) / vec_sum

    return dist
