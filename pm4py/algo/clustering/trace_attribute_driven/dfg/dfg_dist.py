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
from pm4py.algo.discovery.dfg import algorithm as dfg_algorithm
from pm4py.statistics.attributes.log import get as attributes_filter
import pandas as pd
from pm4py.util import pandas_utils
from pm4py.algo.clustering.trace_attribute_driven.variants import act_dist_calc


def dfg_dist_calc_act(log1, log2):
    act1 = attributes_filter.get_attribute_values(log1, "concept:name")
    act2 = attributes_filter.get_attribute_values(log2, "concept:name")
    df1_act = act_dist_calc.occu_var_act(act1)
    df2_act = act_dist_calc.occu_var_act(act2)
    df_act = pandas_utils.merge(df1_act, df2_act, how='outer', on='var').fillna(0)
    dist_act = pdist(np.array([df_act['freq_x'].values, df_act['freq_y'].values]), 'cosine')[0]
    return dist_act


def dfg_dist_calc_suc(log1, log2):
    dfg1 = dfg_algorithm.apply(log1)
    dfg2 = dfg_algorithm.apply(log2)
    df1_dfg = act_dist_calc.occu_var_act(dfg1)
    df2_dfg = act_dist_calc.occu_var_act(dfg2)
    df_dfg = pandas_utils.merge(df1_dfg, df2_dfg, how='outer', on='var').fillna(0)
    dist_dfg = pdist(np.array([df_dfg['freq_x'].values, df_dfg['freq_y'].values]), 'cosine')[0]
    return dist_dfg


def dfg_dist_calc(log1, log2):
    act1 = attributes_filter.get_attribute_values(log1, "concept:name")
    act2 = attributes_filter.get_attribute_values(log2, "concept:name")
    dfg1 = dfg_algorithm.apply(log1)
    dfg2 = dfg_algorithm.apply(log2)
    df1_act = act_dist_calc.occu_var_act(act1)
    df2_act = act_dist_calc.occu_var_act(act2)
    df1_dfg = act_dist_calc.occu_var_act(dfg1)
    df2_dfg = act_dist_calc.occu_var_act(dfg2)
    df_act = pandas_utils.merge(df1_act, df2_act, how='outer', on='var').fillna(0)
    df_dfg = pandas_utils.merge(df1_dfg, df2_dfg, how='outer', on='var').fillna(0)
    dist_act = pdist(np.array([df_act['freq_x'].values, df_act['freq_y'].values]), 'cosine')[0]
    dist_dfg = pdist(np.array([df_dfg['freq_x'].values, df_dfg['freq_y'].values]), 'cosine')[0]
    if (np.isnan(dist_dfg) == True):
        dist_dfg = 1
    return dist_act, dist_dfg


def dfg_dist_calc_minkowski(log1, log2, alpha):
    act1 = attributes_filter.get_attribute_values(log1, "concept:name")
    act2 = attributes_filter.get_attribute_values(log2, "concept:name")
    dfg1 = dfg_algorithm.apply(log1)
    dfg2 = dfg_algorithm.apply(log2)
    df1_act = act_dist_calc.occu_var_act(act1)
    df2_act = act_dist_calc.occu_var_act(act2)
    df1_dfg = act_dist_calc.occu_var_act(dfg1)
    df2_dfg = act_dist_calc.occu_var_act(dfg2)
    df_act = pandas_utils.merge(df1_act, df2_act, how='outer', on='var').fillna(0)
    df_dfg = pandas_utils.merge(df1_dfg, df2_dfg, how='outer', on='var').fillna(0)
    dist_act = pdist(np.array([df_act['freq_x'].values / np.sum(df_act['freq_x'].values),
                               df_act['freq_y'].values / np.sum(df_act['freq_y'].values)]), 'minkowski', p=2.)[0]
    dist_dfg = pdist(np.array([df_dfg['freq_x'].values / np.sum(df_dfg['freq_x'].values),
                               df_dfg['freq_y'].values / np.sum(df_dfg['freq_y'].values)]), 'minkowski', p=2.)[0]
    dist = dist_act * alpha + dist_dfg * (1 - alpha)
    return dist
