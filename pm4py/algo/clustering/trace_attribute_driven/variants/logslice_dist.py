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
from scipy.spatial.distance import pdist
from pm4py.statistics.attributes.log import get as attributes_filter
from pm4py.util import constants, pandas_utils
from pm4py.algo.discovery.dfg.variants import native
import pandas as pd
from pm4py.algo.clustering.trace_attribute_driven.util import filter_subsets
from pm4py.algo.clustering.trace_attribute_driven.variants import act_dist_calc


def log2sublog(log, str):
    tracefilter_log = filter_subsets.apply_trace_attributes(log, [str],
                                                            parameters={
                                                                constants.PARAMETER_CONSTANT_ATTRIBUTE_KEY: "AMOUNT_REQ",
                                                                "positive": True})

    return tracefilter_log


def slice_dist_suc(log_1, log_2, unit):
    (log1_list, freq1_list) = filter_subsets.logslice_percent(log_1, unit)
    (log2_list, freq2_list) = filter_subsets.logslice_percent(log_2, unit)

    if len(freq1_list) >= len(freq2_list):
        max_len = len(freq1_list)
        min_len = len(freq2_list)
        max_log = log1_list
        min_log = log2_list
        var_count_max = freq1_list
        var_count_min = freq2_list

    else:
        max_len = len(freq2_list)
        min_len = len(freq1_list)
        max_log = log2_list
        min_log = log1_list
        var_count_max = freq2_list
        var_count_min = freq1_list

    dist_matrix = np.zeros((max_len, min_len))
    max_per_var = np.zeros(max_len)
    max_freq = np.zeros(max_len)
    min_freq = np.zeros(min_len)
    min_per_var = np.zeros(min_len)
    index_rec = set(list(range(min_len)))

    if log1_list == log2_list:
        print("Please give different variant lists!")
        dist = 0
    else:
        for i in range(max_len):
            dist_vec = np.zeros(min_len)
            dfg1 = native.apply(max_log[i])
            df1_dfg = act_dist_calc.occu_var_act(dfg1)
            for j in range(min_len):
                dfg2 = native.apply(min_log[j])
                df2_dfg = act_dist_calc.occu_var_act(dfg2)
                df_dfg = pandas_utils.merge(df1_dfg, df2_dfg, how='outer', on='var').fillna(0)
                dist_vec[j] = pdist(np.array([df_dfg['freq_x'].values, df_dfg['freq_y'].values]), 'cosine')[0]
                dist_matrix[i][j] = dist_vec[j]
                if j == (min_len - 1):
                    max_loc_col = np.argmin(dist_vec)
                    if abs(dist_vec[max_loc_col]) <= 1e-8:
                        index_rec.discard(max_loc_col)
                        max_freq[i] = var_count_max[i] * var_count_min[max_loc_col] * 2
                        max_per_var[i] = dist_vec[max_loc_col] * max_freq[i] * 2
                    else:
                        max_freq[i] = var_count_max[i] * var_count_min[max_loc_col]
                        max_per_var[i] = dist_vec[max_loc_col] * max_freq[i]

        if (len(index_rec) != 0):
            for i in list(index_rec):
                min_loc_row = np.argmin(dist_matrix[:, i])
                min_freq[i] = var_count_max[min_loc_row] * var_count_min[i]
                min_per_var[i] = dist_matrix[min_loc_row, i] * min_freq[i]
        dist = (np.sum(max_per_var) + np.sum(min_per_var)) / (np.sum(max_freq) + np.sum(min_freq))

    return dist


def slice_dist_act(log_1, log_2, unit, parameters=None):
    (log1_list, freq1_list) = filter_subsets.logslice_percent(log_1, unit)
    (log2_list, freq2_list) = filter_subsets.logslice_percent(log_2, unit)

    if len(freq1_list) >= len(freq2_list):
        max_len = len(freq1_list)
        min_len = len(freq2_list)
        max_log = log1_list
        min_log = log2_list
        var_count_max = freq1_list
        var_count_min = freq2_list

    else:
        max_len = len(freq2_list)
        min_len = len(freq1_list)
        max_log = log2_list
        min_log = log1_list
        var_count_max = freq2_list
        var_count_min = freq1_list

    dist_matrix = np.zeros((max_len, min_len))
    max_per_var = np.zeros(max_len)
    max_freq = np.zeros(max_len)
    min_freq = np.zeros(min_len)
    min_per_var = np.zeros(min_len)
    index_rec = set(list(range(min_len)))

    if log1_list == log2_list:
        print("Please give different variant lists!")
        dist = 0
    else:
        for i in range(max_len):
            dist_vec = np.zeros(min_len)
            act1 = attributes_filter.get_attribute_values(max_log[i], "concept:name")
            df1_act = act_dist_calc.occu_var_act(act1)
            for j in range(min_len):
                act2 = attributes_filter.get_attribute_values(min_log[j], "concept:name")
                df2_act = act_dist_calc.occu_var_act(act2)
                df_act = pandas_utils.merge(df1_act, df2_act, how='outer', on='var').fillna(0)
                dist_vec[j] = pdist(np.array([df_act['freq_x'].values, df_act['freq_y'].values]), 'cosine')[0]
                dist_matrix[i][j] = dist_vec[j]
                if j == (min_len - 1):
                    max_loc_col = np.argmin(dist_vec)
                    if abs(dist_vec[max_loc_col]) <= 1e-8:
                        index_rec.discard(max_loc_col)
                        max_freq[i] = var_count_max[i] * var_count_min[max_loc_col] * 2
                        max_per_var[i] = dist_vec[max_loc_col] * max_freq[i] * 2
                    else:
                        max_freq[i] = var_count_max[i] * var_count_min[max_loc_col]
                        max_per_var[i] = dist_vec[max_loc_col] * max_freq[i]

        if (len(index_rec) != 0):
            for i in list(index_rec):
                min_loc_row = np.argmin(dist_matrix[:, i])
                min_freq[i] = var_count_max[min_loc_row] * var_count_min[i]
                min_per_var[i] = dist_matrix[min_loc_row, i] * min_freq[i]

        dist = (np.sum(max_per_var) + np.sum(min_per_var)) / (np.sum(max_freq) + np.sum(min_freq))

    return dist
