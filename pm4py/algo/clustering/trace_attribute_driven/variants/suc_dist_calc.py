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
import pandas as pd
import numpy as np
from pm4py.algo.clustering.trace_attribute_driven.util import filter_subsets
from scipy.spatial.distance import pdist
from collections import Counter
from pm4py.util import exec_utils, pandas_utils
from enum import Enum
from pm4py.util import constants


class Parameters(Enum):
    ATTRIBUTE_KEY = constants.PARAMETER_CONSTANT_ATTRIBUTE_KEY
    ACTIVITY_KEY = constants.PARAMETER_CONSTANT_ACTIVITY_KEY
    SINGLE = "single"
    BINARIZE = "binarize"
    POSITIVE = "positive"
    LOWER_PERCENT = "lower_percent"



def occu_suc(dfg, filter_percent):
    '''

    :param dfg: a counter containing all the direct succession relationship with frequency
    :param filter_percent: clarify the percentage of direct succession one wants to preserve
    :return: dataframe of direct succession relationship with frequency
    '''

    df = pandas_utils.instantiate_dataframe_from_dict(dict(dfg), orient='index', columns=['freq'])
    df = df.sort_values(axis=0, by=['freq'], ascending=False)
    df = df.reset_index().rename(columns={'index': 'suc'})
    # delete duplicated successions
    df = df.drop_duplicates('suc', keep='first')
    # delete self succession
    # filter out direct succession by percentage
    filter = list(range(0, round(filter_percent * len(df))))
    df = pandas_utils.insert_index(df)
    df = df[df[constants.DEFAULT_INDEX_KEY].isin(filter)].reset_index(drop=True)
    return df


def occu_var_suc(var_list, parameters=None):
    '''
    return dataframe that shows the frequency of each element(direct succession) in each variant list
    :param var_list:
    :param parameters: binarize states if user wants to binarize the frequency, default is binarized
    :return:
    '''
    if parameters is None:
        parameters = {}

    binarize = exec_utils.get_param_value(Parameters.BINARIZE, parameters, True)

    comb_list = [var_list[i] + constants.DEFAULT_VARIANT_SEP + var_list[i + 1] for i in range(len(var_list) - 1)]
    result = Counter(comb_list)  # count number of occurrence of each element
    df = pandas_utils.instantiate_dataframe_from_dict(dict(result), orient='index', columns=['freq'])
    df = df.reset_index().rename(columns={'index': 'direct_suc'})
    if (binarize):
        # Binarize succession frequency (optional)
        df.loc[df.freq > 1, 'freq'] = 1
        return df
    else:
        return df


def suc_sim(var_list_1, var_list_2, log1, log2, freq_thres, num, parameters=None):
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
            df_1 = occu_var_suc(max_var[i], parameters={"binarize": False})
            for j in range(min_len):
                df_2 = occu_var_suc(min_var[j], parameters={"binarize": False})
                df = pandas_utils.merge(df_1, df_2, how='outer', on='direct_suc').fillna(0)
                # cosine similarity is used to calculate trace similarity
                dist_vec[j] = (pdist(np.array([df['freq_x'].values, df['freq_y'].values]), 'cosine')[0])

                dist_matrix[i][j] = dist_vec[j]
                if (single):
                    if abs(dist_vec[j]) <= 1e-8:
                        max_freq[i] = var_count_max.iloc[i] * var_count_min.iloc[j]
                        max_per_var[i] = dist_vec[j] * max_freq[i]

                        break
                    elif j == (min_len - 1):
                        max_loc_col = np.argmin(dist_vec)  # location of max value
                        max_freq[i] = var_count_max.iloc[i] * var_count_min.iloc[max_loc_col]
                        max_per_var[i] = dist_vec[max_loc_col] * max_freq[i]
                else:
                    col_sum[i] += dist_vec[j] * var_count_max.iloc[i] * var_count_min.iloc[j]

    if (single):
        # single linkage
        dist = np.sum(max_per_var) / np.sum(max_freq)
    else:
        vmax_vec = (var_count_max.values).reshape(-1, 1)
        vmin_vec = (var_count_min.values).reshape(1, -1)
        vec_sum = np.sum(np.dot(vmax_vec, vmin_vec))
        dist = np.sum(col_sum) / vec_sum

    return dist


def suc_sim_dual(var_list_1, var_list_2, log1, log2, freq_thres, num, parameters=None):
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
            df_1 = occu_var_suc(max_var[i], parameters={"binarize": False})
            for j in range(min_len):
                df_2 = occu_var_suc(min_var[j], parameters={"binarize": False})
                df = pandas_utils.merge(df_1, df_2, how='outer', on='direct_suc').fillna(0)
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

    if (single):
        # single linkage
        dist = np.sum(max_per_var) / np.sum(max_freq)
    else:
        vmax_vec = (var_count_max.values).reshape(-1, 1)
        vmin_vec = (var_count_min.values).reshape(1, -1)
        vec_sum = np.sum(np.dot(vmax_vec, vmin_vec))
        dist = np.sum(col_sum) / vec_sum

    return dist


def suc_sim_percent(log1, log2, percent_1, percent_2):
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
    col_sum = np.zeros(max_len)
    index_rec = set(list(range(min_len)))

    if var_list_1 == var_list_2:
        dist = 0
    else:
        for i in range(max_len):
            dist_vec = np.zeros(min_len)
            df_1 = occu_var_suc(max_var[i], parameters={"binarize": False})
            for j in range(min_len):
                df_2 = occu_var_suc(min_var[j], parameters={"binarize": False})
                df = pandas_utils.merge(df_1, df_2, how='outer', on='direct_suc').fillna(0)
                # cosine similarity is used to calculate trace similarity
                dist_vec[j] = (pdist(np.array([df['freq_x'].values, df['freq_y'].values]), 'cosine')[0])
                if (np.isnan(dist_vec[j]) == True):
                    dist_vec[j] = 1
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

        # single linkage
        dist = (np.sum(max_per_var) + np.sum(min_per_var)) / (np.sum(max_freq) + np.sum(min_freq))

    return dist


def suc_sim_percent_avg(log1, log2, percent_1, percent_2):
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
        df_1 = occu_var_suc(max_var[i], parameters={"binarize": False})
        for j in range(min_len):
            df_2 = occu_var_suc(min_var[j], parameters={"binarize": False})
            df = pandas_utils.merge(df_1, df_2, how='outer', on='direct_suc').fillna(0)
            # cosine similarity is used to calculate trace similarity
            dist_vec[j] = (pdist(np.array([df['freq_x'].values, df['freq_y'].values]), 'cosine')[0])
            if (np.isnan(dist_vec[j]) == True):
                dist_vec[j] = 1
            dist_matrix[i][j] = dist_vec[j]
            col_sum[i] += dist_vec[j] * var_count_max.iloc[i] * var_count_min.iloc[j]

    # single linkage
    vmax_vec = (var_count_max.values).reshape(-1, 1)
    vmin_vec = (var_count_min.values).reshape(1, -1)
    vec_sum = np.sum(np.dot(vmax_vec, vmin_vec))
    dist = np.sum(col_sum) / vec_sum

    return dist
