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
from pm4py.algo.clustering.trace_attribute_driven.util import filter_subsets
import pandas as pd
import numpy as np
from collections import Counter
from scipy.spatial.distance import pdist
from pm4py.util import exec_utils
from enum import Enum
from pm4py.util import constants, pandas_utils


class Parameters(Enum):
    ATTRIBUTE_KEY = constants.PARAMETER_CONSTANT_ATTRIBUTE_KEY
    ACTIVITY_KEY = constants.PARAMETER_CONSTANT_ACTIVITY_KEY
    SINGLE = "single"
    BINARIZE = "binarize"
    POSITIVE = "positive"
    LOWER_PERCENT = "lower_percent"



def occu_var_act(var_list):
    '''
    return dataframe that shows the frequency of each element(activity) in each variant list
    :param var_list:
    :return:
    '''
    result = Counter(var_list)  # count number of occurrence of each element
    df = pandas_utils.instantiate_dataframe_from_dict(dict(result), orient='index', columns=['freq'])
    df = df.reset_index().rename(columns={'index': 'var'})

    return df


def act_sim(var_list_1, var_list_2, log1, log2, freq_thres, num, parameters=None):
    '''

    this function compare the activity similarity between two sublogs via the two lists of variants.
    :param var_list_1: lists of variants in sublog 1
    :param var_list_2: lists of variants in sublog 2
    :param freq_thres: same as sublog2df()
    :param log1: input sublog1 of sublog2df(), which must correspond to var_list_1
    :param log2: input sublog2 of sublog2df(), which must correspond to var_list_2
    :return: the distance matrix between 2 sublogs in which each element is the distance between two variants.
    '''

    if parameters is None:
        parameters = {}

    single = exec_utils.get_param_value(Parameters.SINGLE, parameters, False)

    if len(var_list_1) >= len(var_list_2):
        max_len = len(var_list_1)
        min_len = len(var_list_2)
        max_var = var_list_1
        min_var = var_list_2
        var_count_max = filter_subsets.sublog2df(log1, freq_thres, num)['count']
        var_count_min = filter_subsets.sublog2df(log2, freq_thres, num)['count']
    else:
        max_len = len(var_list_2)
        min_len = len(var_list_1)
        max_var = var_list_2
        min_var = var_list_1
        var_count_max = filter_subsets.sublog2df(log2, freq_thres, num)['count']
        var_count_min = filter_subsets.sublog2df(log1, freq_thres, num)['count']

    dist_matrix = np.zeros((max_len, min_len))
    max_per_var = np.zeros(max_len)
    max_freq = np.zeros(max_len)
    col_sum = np.zeros(max_len)

    if var_list_1 == var_list_2:
        print("Please give different variant lists!")
    else:
        for i in range(max_len):
            dist_vec = np.zeros(min_len)
            df_1 = occu_var_act(max_var[i])
            for j in range(min_len):
                df_2 = occu_var_act(min_var[j])
                df = pandas_utils.merge(df_1, df_2, how='outer', on='var').fillna(0)
                # cosine similarity is used to calculate trace similarity
                dist_vec[j] = (pdist(np.array([df['freq_x'].values, df['freq_y'].values]), 'cosine')[0])
                dist_matrix[i][j] = dist_vec[j]
                if (single):
                    if abs(dist_vec[j]) <= 1e-6:
                        max_freq[i] = var_count_max.iloc[i] * var_count_min.iloc[j]
                        max_per_var[i] = dist_vec[j] * max_freq[i]
                        break

                    elif j == (min_len - 1):
                        max_loc_col = np.argmin(dist_vec)
                        max_freq[i] = var_count_max.iloc[i] * var_count_min.iloc[max_loc_col]
                        max_per_var[i] = dist_vec[max_loc_col] * max_freq[i]
                else:
                    col_sum[i] += dist_vec[j] * var_count_max.iloc[i] * var_count_min.iloc[j]

    if single:
        dist = np.sum(max_per_var) / np.sum(max_freq)
    else:
        vmax_vec = (var_count_max.values).reshape(-1, 1)
        vmin_vec = (var_count_min.values).reshape(1, -1)
        vec_sum = np.sum(np.dot(vmax_vec, vmin_vec))
        dist = np.sum(col_sum) / vec_sum

    return dist


def act_sim_med(var_list_1, var_list_2, log1, log2, freq_thres, num, parameters=None):
    '''

    this function compare the activity similarity between two sublogs via the two lists of variants.
    :param var_list_1: lists of variants in sublog 1
    :param var_list_2: lists of variants in sublog 2
    :param freq_thres: same as sublog2df()
    :param log1: input sublog1 of sublog2df(), which must correspond to var_list_1
    :param log2: input sublog2 of sublog2df(), which must correspond to var_list_2
    :return: the distance matrix between 2 sublogs in which each element is the distance between two variants.
    '''

    if parameters is None:
        parameters = {}

    if len(var_list_1) >= len(var_list_2):
        max_len = len(var_list_1)
        min_len = len(var_list_2)
        max_var = var_list_1
        min_var = var_list_2
        var_count_max = filter_subsets.sublog2df(log1, freq_thres, num)['count']
        var_count_min = filter_subsets.sublog2df(log2, freq_thres, num)['count']
    else:
        max_len = len(var_list_2)
        min_len = len(var_list_1)
        max_var = var_list_2
        min_var = var_list_1
        var_count_max = filter_subsets.sublog2df(log2, freq_thres, num)['count']
        var_count_min = filter_subsets.sublog2df(log1, freq_thres, num)['count']

    dist_matrix = np.zeros((max_len, min_len))
    max_per_var = np.zeros(max_len)
    max_freq = np.zeros(max_len)

    if var_list_1 == var_list_2:
        print("Please give different variant lists!")
    else:
        for i in range(max_len):
            dist_vec = np.zeros(min_len)
            df_1 = occu_var_act(max_var[i])
            for j in range(min_len):
                df_2 = occu_var_act(min_var[j])
                df = pandas_utils.merge(df_1, df_2, how='outer', on='var').fillna(0)
                # cosine similarity is used to calculate trace similarity
                dist_vec[j] = (pdist(np.array([df['freq_x'].values, df['freq_y'].values]), 'cosine')[0])
                dist_matrix[i][j] = 1 - dist_vec[j]
                if (j == min_len - 1):
                    med_loc = np.argsort(dist_vec)[len(dist_vec) // 2]
                    max_freq[i] = var_count_max.iloc[i] * var_count_min.iloc[med_loc]
                    max_per_var[i] = dist_vec[med_loc] * max_freq[i]

        # single linkage
    dist = np.sum(max_per_var) / np.sum(max_freq)

    return dist


def act_sim_dual(var_list_1, var_list_2, log1, log2, freq_thres, num, parameters=None):
    '''

    this function compare the activity similarity between two sublogs via the two lists of variants.
    :param var_list_1: lists of variants in sublog 1
    :param var_list_2: lists of variants in sublog 2
    :param freq_thres: same as sublog2df()
    :param log1: input sublog1 of sublog2df(), which must correspond to var_list_1
    :param log2: input sublog2 of sublog2df(), which must correspond to var_list_2
    :return: the distance matrix between 2 sublogs in which each element is the distance between two variants.
    '''

    if parameters is None:
        parameters = {}

    single = exec_utils.get_param_value(Parameters.SINGLE, parameters, False)

    if len(var_list_1) >= len(var_list_2):
        max_len = len(var_list_1)
        min_len = len(var_list_2)
        max_var = var_list_1
        min_var = var_list_2
        var_count_max = filter_subsets.sublog2df(log1, freq_thres, num)['count']
        var_count_min = filter_subsets.sublog2df(log2, freq_thres, num)['count']
    else:
        max_len = len(var_list_2)
        min_len = len(var_list_1)
        max_var = var_list_2
        min_var = var_list_1
        var_count_max = filter_subsets.sublog2df(log2, freq_thres, num)['count']
        var_count_min = filter_subsets.sublog2df(log1, freq_thres, num)['count']

    dist_matrix = np.zeros((max_len, min_len))
    max_per_var = np.zeros(max_len)
    max_freq = np.zeros(max_len)
    min_freq = np.zeros(min_len)
    min_per_var = np.zeros(min_len)
    col_sum = np.zeros(max_len)
    index_rec = set(list(range(min_len)))

    if var_list_1 == var_list_2:
        print("Please give different variant lists!")
    else:
        for i in range(max_len):
            dist_vec = np.zeros(min_len)
            df_1 = occu_var_act(max_var[i])
            for j in range(min_len):
                df_2 = occu_var_act(min_var[j])
                df = pandas_utils.merge(df_1, df_2, how='outer', on='var').fillna(0)
                # cosine similarity is used to calculate trace similarity
                dist_vec[j] = (pdist(np.array([df['freq_x'].values, df['freq_y'].values]), 'cosine')[0])
                dist_matrix[i][j] = dist_vec[j]
                if j == (min_len - 1):
                    # max_loc_col = np.argmax(dist_matrix[i, :])  # location of max value
                    max_loc_col = np.argmin(dist_vec)
                    if abs(dist_vec[max_loc_col]) <= 1e-6:
                        index_rec.discard(max_loc_col)
                        max_freq[i] = var_count_max.iloc[i] * var_count_min.iloc[max_loc_col] * 2
                        max_per_var[i] = dist_vec[max_loc_col] * max_freq[i] * 2
                    else:
                        max_freq[i] = var_count_max.iloc[i] * var_count_min.iloc[max_loc_col]
                        max_per_var[i] = dist_vec[max_loc_col] * max_freq[i]

        for i in list(index_rec):
            min_loc_row = np.argmin(dist_matrix[:, i])
            min_freq[i] = var_count_max.iloc[min_loc_row] * var_count_min.iloc[i]
            min_per_var[i] = dist_matrix[min_loc_row, i] * min_freq[i]

    if single:
        dist = (np.sum(max_per_var) + np.sum(min_per_var)) / (np.sum(max_freq) + np.sum(min_freq))
    else:
        vmax_vec = (var_count_max.values).reshape(-1, 1)
        vmin_vec = (var_count_min.values).reshape(1, -1)
        vec_sum = np.sum(np.dot(vmax_vec, vmin_vec))
        dist = np.sum(col_sum) / vec_sum

    return dist


def act_sim_percent(log1, log2, percent_1, percent_2):
    '''

    this function compare the activity similarity between two sublogs via the two lists of variants.
    :param var_list_1: lists of variants in sublog 1
    :param var_list_2: lists of variants in sublog 2
    :param freq_thres: same as sublog2df()
    :param log1: input sublog1 of sublog2df(), which must correspond to var_list_1
    :param log2: input sublog2 of sublog2df(), which must correspond to var_list_2
    :return: the distance matrix between 2 sublogs in which each element is the distance between two variants.
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
            df_1 = occu_var_act(max_var[i])
            for j in range(min_len):
                df_2 = occu_var_act(min_var[j])
                df = pandas_utils.merge(df_1, df_2, how='outer', on='var').fillna(0)
                # cosine similarity is used to calculate trace similarity
                dist_vec[j] = (pdist(np.array([df['freq_x'].values, df['freq_y'].values]), 'cosine')[0])
                dist_matrix[i][j] = dist_vec[j]
                if j == (min_len - 1):
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


def act_sim_percent_avg(log1, log2, percent_1, percent_2):
    '''

    this function compare the activity similarity between two sublogs via the two lists of variants.
    :param var_list_1: lists of variants in sublog 1
    :param var_list_2: lists of variants in sublog 2
    :param freq_thres: same as sublog2df()
    :param log1: input sublog1 of sublog2df(), which must correspond to var_list_1
    :param log2: input sublog2 of sublog2df(), which must correspond to var_list_2
    :return: the distance matrix between 2 sublogs in which each element is the distance between two variants.
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
    col_sum = np.zeros(max_len)

    for i in range(max_len):
        dist_vec = np.zeros(min_len)
        df_1 = occu_var_act(max_var[i])
        for j in range(min_len):
            df_2 = occu_var_act(min_var[j])
            df = pandas_utils.merge(df_1, df_2, how='outer', on='var').fillna(0)
            dist_vec[j] = (pdist(np.array([df['freq_x'].values, df['freq_y'].values]), 'cosine')[0])
            col_sum[i] += dist_vec[j] * var_count_max.iloc[i] * var_count_min.iloc[j]
            dist_matrix[i][j] = dist_vec[j]

    vmax_vec = (var_count_max.values).reshape(-1, 1)
    vmin_vec = (var_count_min.values).reshape(1, -1)
    vec_sum = np.sum(np.dot(vmax_vec, vmin_vec))
    dist = np.sum(col_sum) / vec_sum

    return dist


def act_sim_percent_avg_actset(log1, log2, percent_1, percent_2, actset):
    '''

    this function compare the activity similarity between two sublogs via the two lists of variants.
    :param var_list_1: lists of variants in sublog 1
    :param var_list_2: lists of variants in sublog 2
    :param freq_thres: same as sublog2df()
    :param log1: input sublog1 of sublog2df(), which must correspond to var_list_1
    :param log2: input sublog2 of sublog2df(), which must correspond to var_list_2
    :return: the distance matrix between 2 sublogs in which each element is the distance between two variants.
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
    col_sum = np.zeros(max_len)

    for i in range(max_len):
        dist_vec = np.zeros(min_len)
        df_1 = occu_var_act(max_var[i])
        df_1 = pandas_utils.merge(actset['var'], df_1, how='outer', on='var').fillna(0)
        for j in range(min_len):
            df_2 = occu_var_act(min_var[j])
            df = pandas_utils.merge(df_1, df_2, how='outer', on='var').fillna(0)
            # cosine similarity is used to calculate trace similarity
            dist_vec[j] = (pdist(np.array([df['freq_x'].values, df['freq_y'].values]), 'cosine')[0])
            col_sum[i] += dist_vec[j] * var_count_max.iloc[i] * var_count_min.iloc[j]
            dist_matrix[i][j] = dist_vec[j]

    vmax_vec = (var_count_max.values).reshape(-1, 1)
    vmin_vec = (var_count_min.values).reshape(1, -1)
    vec_sum = np.sum(np.dot(vmax_vec, vmin_vec))
    dist = np.sum(col_sum) / vec_sum

    return dist
