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
from pm4py.algo.clustering.trace_attribute_driven.variants import act_dist_calc, suc_dist_calc
from pm4py.algo.clustering.trace_attribute_driven.util import filter_subsets
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



def inner_prod_calc(df):
    innerprod = ((df.loc[:, 'freq_x']) * (df.loc[:, 'freq_y'])).sum()
    sqrt_1 = np.sqrt(((df.loc[:, 'freq_x']) ** 2).sum())
    sqrt_2 = np.sqrt(((df.loc[:, 'freq_y']) ** 2).sum())
    return innerprod, sqrt_1, sqrt_2


def dist_calc(var_list_1, var_list_2, log1, log2, freq_thres, num, alpha, parameters=None):
    '''
    this function compare the activity similarity between two sublogs via the two lists of variants.
    :param var_list_1: lists of variants in sublog 1
    :param var_list_2: lists of variants in sublog 2
    :param freq_thres: same as sublog2df()
    :param log1: input sublog1 of sublog2df(), which must correspond to var_list_1
    :param log2: input sublog2 of sublog2df(), which must correspond to var_list_2
    :param alpha: the weight parameter between activity similarity and succession similarity, which belongs to (0,1)
    :param parameters: state which linkage method to use
    :return: the similarity value between two sublogs
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

    # act
    max_per_var_act = np.zeros(max_len)
    max_freq_act = np.zeros(max_len)
    col_sum_act = np.zeros(max_len)

    # suc
    max_per_var_suc = np.zeros(max_len)
    col_sum_suc = np.zeros(max_len)
    max_freq_suc = np.zeros(max_len)

    if var_list_1 == var_list_2:
        print("Please give different variant lists!")
    else:
        for i in range(max_len):
            dist_vec_act = np.zeros(min_len)
            dist_vec_suc = np.zeros(min_len)
            df_1_act = act_dist_calc.occu_var_act(max_var[i])
            df_1_suc = suc_dist_calc.occu_var_suc(max_var[i], parameters={"binarize": True})
            for j in range(min_len):
                df_2_act = act_dist_calc.occu_var_act(min_var[j])
                df_2_suc = suc_dist_calc.occu_var_suc(min_var[j], parameters={"binarize": True})

                df_act = pandas_utils.merge(df_1_act, df_2_act, how='outer', on='var').fillna(0)
                df_suc = pandas_utils.merge(df_1_suc, df_2_suc, how='outer', on='direct_suc').fillna(0)

                dist_vec_act[j] = (pdist(np.array([df_act['freq_x'].values, df_act['freq_y'].values]), 'cosine')[0])
                dist_vec_suc[j] = (pdist(np.array([df_suc['freq_x'].values, df_suc['freq_y'].values]), 'cosine')[0])

                if (single):
                    if (abs(dist_vec_act[j]) <= 1e-8) and (abs(dist_vec_suc[j]) <= 1e-6):  # ensure both are 1
                        max_freq_act[i] = var_count_max.iloc[i] * var_count_min.iloc[j]
                        max_freq_suc[i] = max_freq_act[i]
                        max_per_var_act[i] = dist_vec_act[j] * max_freq_act[i]
                        max_per_var_suc[i] = dist_vec_suc[j] * max_freq_suc[i]

                        break
                    elif j == (min_len - 1):
                        max_loc_col_act = np.argmin(dist_vec_act)  # location of max value
                        max_loc_col_suc = np.argmin(dist_vec_suc)  # location of max value
                        max_freq_act[i] = var_count_max.iloc[i] * var_count_min.iloc[max_loc_col_act]
                        max_freq_suc[i] = var_count_max.iloc[i] * var_count_min.iloc[max_loc_col_suc]
                        max_per_var_act[i] = dist_vec_act[max_loc_col_act] * max_freq_act[i]
                        max_per_var_suc[i] = dist_vec_suc[max_loc_col_suc] * max_freq_suc[i]

                else:
                    col_sum_act[i] += dist_vec_act[j] * var_count_max.iloc[i] * var_count_min.iloc[j]
                    col_sum_suc[i] += dist_vec_suc[j] * var_count_max.iloc[i] * var_count_min.iloc[j]
    if (single):
        # single linkage
        dist_act = np.sum(max_per_var_act) / np.sum(max_freq_act)
        dist_suc = np.sum(max_per_var_suc) / np.sum(max_freq_suc)
        dist = dist_act * alpha + dist_suc * (1 - alpha)
    else:
        vmax_vec = (var_count_max.values).reshape(-1, 1)
        vmin_vec = (var_count_min.values).reshape(1, -1)
        vec_sum = np.sum(np.dot(vmax_vec, vmin_vec))
        dist = (np.sum(col_sum_act) * alpha + np.sum(col_sum_suc) * (1 - alpha)) / vec_sum

    return dist
