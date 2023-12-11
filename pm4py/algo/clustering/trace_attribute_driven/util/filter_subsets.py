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
from collections import Counter
from pm4py.objects.log.obj import EventLog, Trace
from pm4py.objects.log.util.xes import DEFAULT_NAME_KEY
from pm4py.statistics.traces.generic.log import case_statistics
from pm4py.statistics.variants.log import get as variants_statistics
from pm4py.util import exec_utils
from pm4py.util import variants_util
from enum import Enum
from pm4py.util import constants, pandas_utils


class Parameters(Enum):
    ATTRIBUTE_KEY = constants.PARAMETER_CONSTANT_ATTRIBUTE_KEY
    ACTIVITY_KEY = constants.PARAMETER_CONSTANT_ACTIVITY_KEY
    SINGLE = "single"
    BINARIZE = "binarize"
    POSITIVE = "positive"
    LOWER_PERCENT = "lower_percent"



def apply_trace_attributes(log, list_of_values, parameters=None):
    """
    Filter log by keeping only traces that has/has not certain case attribute value that belongs to the provided
    values list

    Parameters
    -----------
    log
        Trace log
    values
        Allowed attribute values(if it's numerical value, [] is needed to make it a list)
    parameters
        Parameters of the algorithm, including:
            activity_key -> Attribute identifying the case in the log
            positive -> Indicate if events should be kept/removed

    Returns
    -----------
    filtered_log
        Filtered log
    """
    if parameters is None:
        parameters = {}

    attribute_key = exec_utils.get_param_value(Parameters.ATTRIBUTE_KEY, parameters, DEFAULT_NAME_KEY)
    positive = exec_utils.get_param_value(Parameters.POSITIVE, parameters, True)

    filtered_log = EventLog()
    for trace in log:
        new_trace = Trace()

        found = False
        if attribute_key in trace.attributes:
            attribute_value = trace.attributes[attribute_key]
            if attribute_value in list_of_values:
                found = True

        if (found and positive) or (not found and not positive):
            new_trace = trace
        else:
            for attr in trace.attributes:
                new_trace.attributes[attr] = trace.attributes[attr]

        if len(new_trace) > 0:
            filtered_log.append(new_trace)
    return filtered_log


def sublog2varlist(log, freq_thres, num):
    '''
    extract lists of variants from selected sublogs together with frequency threshold to filter out infrequent variants
    :param log: sublog containing the selected case attribute value
    :param freq_thres: (int) frequency threshold to filter out infrequent variants
    :return: lists of variant strings
    '''
    variants_count = case_statistics.get_variant_statistics(log)
    variants_count = sorted(variants_count, key=lambda x: x['count'], reverse=True)
    filtered_var_list = []
    filtered_var_list_1 = []
    filtered_var_list_2 = []
    for i in range(len(variants_count)):
        if variants_count[i]['count'] >= freq_thres:
            filtered_var_list_1.append(variants_count[i]['variant'])  # variant string
        elif i < num:
            filtered_var_list_2.append(variants_count[i]['variant'])

    # union set ensure the ordered union will be satisfied
    filtered_var_list = filtered_var_list_1 + filtered_var_list_2
    str_var_list = [variants_util.get_activities_from_variant(v) for v in filtered_var_list]

    return str_var_list


def sublog_percent(log, upper_percent, parameters=None):
    '''
    change variant dictionary got from sublog into dataframe, so that we can extract the frequency of each variant
    :param log: same as sublog2varlist()
    :param freq_thres: same as sublog2varlist()
    :return: dataframe of variants with their counts together with the correspond var_list(until the percent )
    '''

    if parameters is None:
        parameters = {}
    lower_percent = exec_utils.get_param_value(Parameters.LOWER_PERCENT, parameters, 0)

    variants_count = case_statistics.get_variant_statistics(log)
    variants_count = sorted(variants_count, key=lambda x: x['count'], reverse=True)
    df = pandas_utils.instantiate_dataframe_from_dict(variants_count)
    # calculate the cumunative sum
    csum = np.array(df['count']).cumsum()
    csum = csum / csum[-1]
    num_list = csum[csum <= upper_percent]
    num_list_lower = csum[csum <= lower_percent]
    # stop until the percent is satisfied
    df_w_count = df.iloc[len(num_list_lower):len(num_list), :]
    # get correspond var_list
    filtered_var_list = df_w_count['variant'].values.tolist()
    str_var_list = [variants_util.get_activities_from_variant(v) for v in filtered_var_list]

    return df_w_count, str_var_list


def sublog_percent2actlist(log, upper_percent, parameters=None):
    '''
    just need to var list
    :param log: same as sublog2varlist()
    :param freq_thres: same as sublog2varlist()
    :return: dataframe of variants with their counts together with the correspond var_list(until the percent )
    '''

    if parameters is None:
        parameters = {}
    lower_percent = exec_utils.get_param_value(Parameters.LOWER_PERCENT, parameters, 0)

    variants_count = case_statistics.get_variant_statistics(log)
    variants_count = sorted(variants_count, key=lambda x: x['count'], reverse=True)
    df = pandas_utils.instantiate_dataframe_from_dict(variants_count)
    # calculate the cumunative sum
    csum = np.array(df['count']).cumsum()
    csum = csum / csum[-1]
    num_list = csum[csum <= upper_percent]
    num_list_lower = csum[csum <= lower_percent]
    # stop until the percent is satisfied
    df_w_count = df.iloc[len(num_list_lower):len(num_list), :]
    # get correspond var_list
    filtered_var_list = df_w_count['variant'].values.tolist()
    str_var_list = [variants_util.get_activities_from_variant(v) for v in filtered_var_list]

    return df_w_count, str_var_list


def sublog_percent2varlist(log, upper_percent, parameters=None):
    '''
    just need to var list
    :param log: same as sublog2varlist()
    :param freq_thres: same as sublog2varlist()
    :return: dataframe of variants with their counts together with the correspond var_list(until the percent )
    '''

    if parameters is None:
        parameters = {}
    lower_percent = exec_utils.get_param_value(Parameters.LOWER_PERCENT, parameters, 0)

    variants_count = case_statistics.get_variant_statistics(log)
    variants_count = sorted(variants_count, key=lambda x: x['count'], reverse=True)
    df = pandas_utils.instantiate_dataframe_from_dict(variants_count)
    # calculate the cumunative sum
    csum = np.array(df['count']).cumsum()
    csum = csum / csum[-1]
    num_list = csum[csum <= upper_percent]
    num_list_lower = csum[csum <= lower_percent]
    # stop until the percent is satisfied
    df_w_count = df.iloc[len(num_list_lower):len(num_list), :]
    # get correspond var_list
    filtered_var_list = df_w_count['variant'].values.tolist()
    return df_w_count, filtered_var_list


def logslice_percent_act(log, unit):
    '''
    slice the actlist per unit percent
    :param log:
    :param unit:
    :return:
    '''
    loglist = []
    freq_list = []
    sup = int(1 / unit)
    num_list = np.array(range(0, sup)) * unit

    for i in range(len(num_list)):
        (df, act_list) = sublog_percent2actlist(log, num_list[i] + unit, parameters={"lower_percent": num_list[i]})
        if len(act_list) != 0:
            sum1 = np.array(df['count']).sum()
            loglist.append(act_list)
            freq_list.append(sum1)
    return loglist, freq_list


def apply_variants_filter(log, admitted_variants, parameters=None):
    """
    Filter log keeping/removing only provided variants

    Parameters
    -----------
    log
        Log object
    admitted_variants
        Admitted variants
    parameters
        Parameters of the algorithm, including:
            activity_key -> Attribute identifying the activity in the log
            positive -> Indicate if events should be kept/removed
    """

    if parameters is None:
        parameters = {}
    positive = exec_utils.get_param_value(Parameters.POSITIVE, parameters, True)
    variants = variants_statistics.get_variants(log, parameters=parameters)
    log = EventLog()
    for variant in variants:
        if (positive and variant in admitted_variants) or (not positive and variant not in admitted_variants):
            for trace in variants[variant]:
                log.append(trace)
    return log


def logslice_percent(log, unit):
    '''
    slice the log per unit percent
    :param log:
    :param unit:
    :return:
    '''
    loglist = []
    freq_list = []
    sup = int(1 / unit)
    num_list = np.array(range(0, sup)) * unit

    for i in range(len(num_list)):
        (df, var_list) = sublog_percent2varlist(log, num_list[i] + unit, parameters={"lower_percent": num_list[i]})
        if len(var_list) != 0:
            log1 = apply_variants_filter(log, var_list, parameters={"positive": True})
            sum1 = np.array(df['count']).sum()
            loglist.append(log1)
            freq_list.append(sum1)

    return loglist, freq_list


def sublog2df_num(log, num):
    '''
    change variant dictionary got from sublog into dataframe, so that we can extract the frequency of each variant
    :param log: same as sublog2varlist()
    :param freq_thres: same as sublog2varlist()
    :return: dataframe of variants with their counts
    '''
    variants_count = case_statistics.get_variant_statistics(log)
    variants_count = sorted(variants_count, key=lambda x: x['count'], reverse=True)
    df = pandas_utils.instantiate_dataframe_from_dict(variants_count)
    df_w_count = df.iloc[0:num, :]
    return df_w_count


def sublog2df(log, freq_thres, num):
    '''
    change variant dictionary got from sublog into dataframe, so that we can extract the frequency of each variant
    :param log: same as sublog2varlist()
    :param freq_thres: same as sublog2varlist()
    :return: dataframe of variants with their counts
    '''
    variants_count = case_statistics.get_variant_statistics(log)
    variants_count = sorted(variants_count, key=lambda x: x['count'], reverse=True)
    df = pandas_utils.instantiate_dataframe_from_dict(variants_count)
    df_w_count_1 = df[df['count'] >= freq_thres]
    df_w_count_2 = df.iloc[0:num, :]
    # take union of two dataframes
    df_w_count = pandas_utils.merge(df_w_count_1, df_w_count_2, how='outer', on=['variant', 'count'])
    # display(df_w_count['variant'])
    return df_w_count


def act_dist(var_list_1, var_list_2, log1, log2, freq_thres):
    '''

    this function compare the activity similarity between two sublogs via the two lists of variants.
    :param var_list_1: lists of variants in sublog 1
    :param var_list_2: lists of variants in sublog 2
    :param freq_thres: same as sublog2df()
    :param log1: input sublog1 of sublog2df(), which must correspond to var_list_1
    :param log2: input sublog2 of sublog2df(), which must correspond to var_list_2
    :return: the distance matrix between 2 sublogs in which each element is the distance between two variants.
    '''

    if len(var_list_1) >= len(var_list_2):
        max_len = len(var_list_1)
        min_len = len(var_list_2)
        max_var = var_list_1
        min_var = var_list_2
        var_count_max = sublog2df(log1, freq_thres)['count']
        var_count_min = sublog2df(log2, freq_thres)['count']
    else:
        max_len = len(var_list_2)
        min_len = len(var_list_1)
        max_var = var_list_2
        min_var = var_list_1
        var_count_max = sublog2df(log2, freq_thres)['count']
        var_count_min = sublog2df(log1, freq_thres)['count']

    dist_matrix = np.zeros((max_len, min_len))

    for i in range(max_len):
        if i < min_len:
            for j in range(0, i + 1):
                result = Counter(max_var[i])  # count number of occurrence of each element
                df_1 = pandas_utils.instantiate_dataframe_from_dict(dict(result), orient='index',
                                              columns=['freq_1'])  # convert dict to dataframe
                df_1 = df_1.reset_index().rename(columns={'index': 'var'})
                result = Counter(min_var[j])  # count number of occurrence of each element
                df_2 = pandas_utils.instantiate_dataframe_from_dict(dict(result), orient='index', columns=['freq_2'])
                df_2 = df_2.reset_index().rename(columns={'index': 'var'})
                df = pandas_utils.merge(df_1, df_2, how='outer', on='var').fillna(
                    0)  # merge two variants and replace empty value by zero
                df['prod'] = df.apply(lambda x: x['freq_1'] * x['freq_2'], axis=1)
                df['sq_1'] = df.apply(lambda x: x['freq_1'] ** 2, axis=1)
                df['sq_2'] = df.apply(lambda x: x['freq_2'] ** 2, axis=1)
                innerprod = df['prod'].sum()
                sqrt_1 = np.sqrt(df['sq_1'].sum())
                sqrt_2 = np.sqrt(df['sq_2'].sum())
                # dist_matrix[i][j] = innerprod / (sqrt_1 * sqrt_2)
                dist_matrix[i][j] = (innerprod / (sqrt_1 * sqrt_2)) * var_count_max.iloc[i] * var_count_min.iloc[
                    j]  # weighted with trace frequency
                dist_matrix[j][i] = dist_matrix[i][j]
        if i >= min_len:
            for j in range(min_len):
                result = Counter(max_var[i])  # count number of occurrence of each element
                df_1 = pandas_utils.instantiate_dataframe_from_dict(dict(result), orient='index', columns=['freq_1'])
                df_1 = df_1.reset_index().rename(columns={'index': 'var'})
                result = Counter(min_var[j])  # count number of occurrence of each element
                df_2 = pandas_utils.instantiate_dataframe_from_dict(dict(result), orient='index', columns=['freq_2'])
                df_2 = df_2.reset_index().rename(columns={'index': 'var'})
                df = pandas_utils.merge(df_1, df_2, how='outer', on='var').fillna(0)
                df['prod'] = df.apply(lambda x: x['freq_1'] * x['freq_2'], axis=1)
                df['sq_1'] = df.apply(lambda x: x['freq_1'] ** 2, axis=1)
                df['sq_2'] = df.apply(lambda x: x['freq_2'] ** 2, axis=1)
                innerprod = df['prod'].sum()
                sqrt_1 = np.sqrt(df['sq_1'].sum())
                sqrt_2 = np.sqrt(df['sq_2'].sum())
                # dist_matrix[i][j] = innerprod / (sqrt_1 * sqrt_2)
                dist_matrix[i][j] = (innerprod / (sqrt_1 * sqrt_2)) * var_count_max.iloc[i] * var_count_min.iloc[
                    j]  # weighted with trace frequency
    if len(var_list_1) >= len(var_list_2):
        dist_matrix = dist_matrix
    else:
        dist_matrix = np.transpose(dist_matrix)

    return dist_matrix
