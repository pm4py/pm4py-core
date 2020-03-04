import pandas as pd
import numpy as np
from collections import Counter
from pm4py.objects.log.importer.xes import factory as xes_importer
from pm4py.objects.log.log import EventLog, Trace
from pm4py.util.constants import PARAMETER_CONSTANT_ATTRIBUTE_KEY
from pm4py.objects.log.util.xes import DEFAULT_NAME_KEY
from pm4py.algo.filtering.log.variants import variants_filter
from pm4py.statistics.traces.log import case_statistics


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

    attribute_key = parameters[
        PARAMETER_CONSTANT_ATTRIBUTE_KEY] if PARAMETER_CONSTANT_ATTRIBUTE_KEY in parameters else DEFAULT_NAME_KEY
    positive = parameters["positive"] if "positive" in parameters else True

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
    # print(filtered_var_list)
    str_var_list = []
    for str in filtered_var_list:
        str_var_list.extend([str.split(',')])
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
    lower_percent = parameters[
        "lower_percent"] if "lower_percent" in parameters else 0

    variants_count = case_statistics.get_variant_statistics(log)
    # print("variants_count", variants_count)
    variants_count = sorted(variants_count, key=lambda x: x['count'], reverse=True)
    # print("variants_count",variants_count)
    df = pd.DataFrame.from_dict(variants_count)
    # print("df",df)
    # calculate the cumunative sum
    csum = np.array(df['count']).cumsum()
    csum = csum / csum[-1]
    # print(csum)
    num_list = csum[csum <= upper_percent]
    num_list_lower = csum[csum <= lower_percent]
    #print(num_list)
    #print(num_list_lower)
    # stop until the percent is satisfied
    df_w_count = df.iloc[len(num_list_lower):len(num_list), :]
    #print(len(df_w_count))
    # get correspond var_list
    filtered_var_list = df_w_count['variant'].values.tolist()
    str_var_list = []
    for str in filtered_var_list:
        str_var_list.extend([str.split(',')])
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
    lower_percent = parameters[
        "lower_percent"] if "lower_percent" in parameters else 0

    variants_count = case_statistics.get_variant_statistics(log)
    variants_count = sorted(variants_count, key=lambda x: x['count'], reverse=True)
    df = pd.DataFrame.from_dict(variants_count)
    # calculate the cumunative sum
    csum = np.array(df['count']).cumsum()
    csum = csum / csum[-1]
    # print(csum)
    num_list = csum[csum <= upper_percent]
    num_list_lower = csum[csum <= lower_percent]
    #print(num_list)
    #print(num_list_lower)
    # stop until the percent is satisfied
    df_w_count = df.iloc[len(num_list_lower):len(num_list), :]
    #print(len(df_w_count))
    # get correspond var_list
    filtered_var_list = df_w_count['variant'].values.tolist()
    str_var_list = []
    for str in filtered_var_list:
        str_var_list.extend(str.split(','))
    #print(str_var_list)
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
    lower_percent = parameters[
        "lower_percent"] if "lower_percent" in parameters else 0

    variants_count = case_statistics.get_variant_statistics(log)
    variants_count = sorted(variants_count, key=lambda x: x['count'], reverse=True)
    df = pd.DataFrame.from_dict(variants_count)
    # calculate the cumunative sum
    csum = np.array(df['count']).cumsum()
    csum = csum / csum[-1]
    # print(csum)
    num_list = csum[csum <= upper_percent]
    num_list_lower = csum[csum <= lower_percent]
    #print(num_list)
    #print(num_list_lower)
    # stop until the percent is satisfied
    df_w_count = df.iloc[len(num_list_lower):len(num_list), :]
    #print(len(df_w_count))
    # get correspond var_list
    filtered_var_list = df_w_count['variant'].values.tolist()
    return df_w_count, filtered_var_list


def logslice_percent_act(log,unit):
    '''
    slice the actlist per unit percent
    :param log:
    :param unit:
    :return:
    '''
    loglist = []
    freq_list = []
    sup = int(1/unit)
    num_list = np.array(range(0,sup))*unit

    #print(num_list)
    for i in range(len(num_list)):
        (df, act_list) = sublog_percent2actlist(log,num_list[i]+unit,parameters={"lower_percent":num_list[i]})
        #print(df)
        if len(act_list)!=0:
            #print([num_list[i],variants_count])
            sum1 = np.array(df['count']).sum()
            #print([num_list[i],sum1])
            loglist.append(act_list)
            freq_list.append(sum1)
            #print([sum1, act_list])
    return loglist,freq_list

def logslice_percent(log,unit):
    '''
    slice the log per unit percent
    :param log:
    :param unit:
    :return:
    '''
    loglist = []
    freq_list = []
    sup = int(1/unit)
    num_list = np.array(range(0,sup))*unit

    #print(num_list)
    for i in range(len(num_list)):
        (df, var_list) = sublog_percent2varlist(log,num_list[i]+unit,parameters={"lower_percent":num_list[i]})
        #print(df)
        if len(var_list)!=0:
            log1 = variants_filter.apply(log, var_list, parameters={"positive": True})
            #print([num_list[i],variants_count])
            sum1 = np.array(df['count']).sum()
            #print([num_list[i],sum1])
            loglist.append(log1)
            freq_list.append(sum1)

    return loglist,freq_list





def sublog2df_num(log, num):
    '''
    change variant dictionary got from sublog into dataframe, so that we can extract the frequency of each variant
    :param log: same as sublog2varlist()
    :param freq_thres: same as sublog2varlist()
    :return: dataframe of variants with their counts
    '''
    variants_count = case_statistics.get_variant_statistics(log)
    variants_count = sorted(variants_count, key=lambda x: x['count'], reverse=True)
    df = pd.DataFrame.from_dict(variants_count)
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
    df = pd.DataFrame.from_dict(variants_count)
    df_w_count_1 = df[df['count'] >= freq_thres]
    df_w_count_2 = df.iloc[0:num, :]
    # take union of two dataframes
    df_w_count = pd.merge(df_w_count_1, df_w_count_2, how='outer', on=['variant', 'count'])
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
                df_1 = pd.DataFrame.from_dict(dict(result), orient='index',
                                              columns=['freq_1'])  # convert dict to dataframe
                df_1 = df_1.reset_index().rename(columns={'index': 'var'})
                result = Counter(min_var[j])  # count number of occurrence of each element
                df_2 = pd.DataFrame.from_dict(dict(result), orient='index', columns=['freq_2'])
                df_2 = df_2.reset_index().rename(columns={'index': 'var'})
                df = pd.merge(df_1, df_2, how='outer', on='var').fillna(
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
                df_1 = pd.DataFrame.from_dict(dict(result), orient='index', columns=['freq_1'])
                df_1 = df_1.reset_index().rename(columns={'index': 'var'})
                result = Counter(min_var[j])  # count number of occurrence of each element
                df_2 = pd.DataFrame.from_dict(dict(result), orient='index', columns=['freq_2'])
                df_2 = df_2.reset_index().rename(columns={'index': 'var'})
                df = pd.merge(df_1, df_2, how='outer', on='var').fillna(0)
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
