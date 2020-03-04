from pm4py.algo.clustering.hierarchical_attribute_based.util import filter_subsets
import pandas as pd
import numpy as np
from collections import Counter
from scipy.spatial.distance import pdist


def occu_var_act(var_list):
    '''
    return dataframe that shows the frequency of each element(activity) in each variant list
    :param var_list:
    :return:
    '''
    result = Counter(var_list)  # count number of occurrence of each element
    df = pd.DataFrame.from_dict(dict(result), orient='index', columns=['freq'])
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

    single = parameters["single"] if "single" in parameters else False

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
    print("list1:", len(max_var))
    print("list2:", len(min_var))

    # print(np.array(var_count_max))
    # print((var_count_min))
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
                df = pd.merge(df_1, df_2, how='outer', on='var').fillna(0)
                #print(df)
                # cosine similarity is used to calculate trace similarity
                dist_vec[j] = (pdist(np.array([df['freq_x'].values, df['freq_y'].values]), 'cosine')[0])
                '''
                #avoid using apply()
                df['prod'] = df.apply(lambda x: x['freq_x'] * x['freq_y'], axis=1)
                df['sq_1'] = df.apply(lambda x: x['freq_x'] ** 2, axis=1)
                df['sq_2'] = df.apply(lambda x: x['freq_y'] ** 2, axis=1)
                innerprod = df['prod'].sum()
                sqrt_1 = np.sqrt(df['sq_1'].sum())
                sqrt_2 = np.sqrt(df['sq_2'].sum())
                
                innerprod = ((df.loc[:, 'freq_x']) * (df.loc[:, 'freq_y'])).sum()
                sqrt_1 = np.sqrt(((df.loc[:, 'freq_x']) ** 2).sum())
                sqrt_2 = np.sqrt(((df.loc[:, 'freq_y']) ** 2).sum())
                '''
                # print(innerprod)
                # dist_vec[j] = innerprod / (sqrt_1 * sqrt_2)
                dist_matrix[i][j] = dist_vec[j]
                if (single):
                    # dist_matrix[i][j] = innerprod / (sqrt_1 * sqrt_2)
                    if abs(dist_vec[j]) <= 1e-6:
                        # print("\n")
                        # max_per_var[i] = dist_vec[j]
                        # max_per_var[i] = dist_matrix[i][j] * var_count_max.iloc[i] * var_count_min.iloc[j]
                        max_freq[i] = var_count_max.iloc[i] * var_count_min.iloc[j]
                        max_per_var[i] = dist_vec[j] * max_freq[i]
                        #print([i,j])
                        break

                    elif j == (min_len - 1):
                        # max_loc_col = np.argmax(dist_matrix[i, :])  # location of max value
                        max_loc_col = np.argmin(dist_vec)
                        #print([i,max_loc_col])
                        # print(type(dist_vec)) # location of max value
                        # print([i,max_loc_col])
                        # max_per_var[i] = dist_vec[max_loc_col]
                        # max_per_var[i] = dist_matrix[i][max_loc_col] * var_count_max.iloc[i] * var_count_min.iloc[
                        #    max_loc_col]
                        max_freq[i] = var_count_max.iloc[i] * var_count_min.iloc[max_loc_col]
                        max_per_var[i] = dist_vec[max_loc_col] * max_freq[i]

                        # print([i,max_loc_col])
                else:
                    # dist_matrix[i][j] = (innerprod / (sqrt_1 * sqrt_2)) * var_count_max.iloc[i] * var_count_min.iloc[
                    # j]  # weighted with trace frequency
                    '''
                    med_loc = np.argsort(dist_vec)[len(dist_vec)//2]
                    max_freq[i] = var_count_max.iloc[i] * var_count_min.iloc[med_loc]
                    max_per_var[i] = dist_vec[med_loc] * max_freq[i]
                    '''
                    col_sum[i] += dist_vec[j] * var_count_max.iloc[i] * var_count_min.iloc[j]
                    # print([i,j,var_count_max.iloc[i] * var_count_min.iloc[j]])
                    # print(col_sum[i])
                    # col_sum[i] += dist_vec[j]
                    # vec_sum += var_count_max.iloc[i] * var_count_min.iloc[j]

                '''
                if dist_matrix[i][j] == 1:
                    #max_per_var[i] = dist_matrix[i][j]
                    max_per_var[i] = dist_matrix[i][j] * var_count_max.iloc[i] * var_count_min.iloc[j]
                    break
                elif j == (min_len - 1):
                    max_loc_col = np.argmax(dist_matrix[i, :])  # location of max value
                    #max_per_var[i] = dist_matrix[i][max_loc_col]
                    max_per_var[i] = dist_matrix[i][max_loc_col] * var_count_max.iloc[i] * var_count_min.iloc[
                        max_loc_col]'''

                '''
                max is np.array[size: len_max]
                if dist =1 
                max = fre1*freq2*dist
                else 
                dist_max = findmax[dist[i,:]
                max = fre1[i]*freq2[j]*dist_max
                '''
    '''           

    else:
        for i in range(max_len):
            df_1 = occu_var_act(max_var[i])
            for j in range(0, i + 1):
                df_2 = occu_var_act(min_var[j])
                df = pd.merge(df_1, df_2, how='outer', on='var').fillna(0)
                df['prod'] = df.apply(lambda x: x['freq_x'] * x['freq_y'], axis=1)
                df['sq_1'] = df.apply(lambda x: x['freq_x'] ** 2, axis=1)
                df['sq_2'] = df.apply(lambda x: x['freq_y'] ** 2, axis=1)
                innerprod = df['prod'].sum()
                sqrt_1 = np.sqrt(df['sq_1'].sum())
                sqrt_2 = np.sqrt(df['sq_2'].sum())
                dist_matrix[i][j] = innerprod / (sqrt_1 * sqrt_2)
                # dist_matrix[i][j] = (innerprod / (sqrt_1 * sqrt_2)) * var_count_max.iloc[i] * var_count_min.iloc[
                #   j]  # weighted with trace frequency
                dist_matrix[j][i] = dist_matrix[i][j]


            if i < min_len:
            for j in range(0, i + 1):
                result = Counter(max_var[i])  # count number of occurrence of each element
                df_1 = pd.DataFrame.from_dict(dict(result), orient='index', columns=['freq_1']) # convert dict to dataframe
                df_1 = df_1.reset_index().rename(columns={'index': 'var'})
                result = Counter(min_var[j])  # count number of occurrence of each element
                df_2 = pd.DataFrame.from_dict(dict(result), orient='index', columns=['freq_2'])
                df_2 = df_2.reset_index().rename(columns={'index': 'var'})
                df = pd.merge(df_1, df_2, how='outer', on='var').fillna(0) # merge two variants and replace empty value by zero
                df['prod'] = df.apply(lambda x: x['freq_1'] * x['freq_2'], axis=1)
                df['sq_1'] = df.apply(lambda x: x['freq_1'] ** 2, axis=1)
                df['sq_2'] = df.apply(lambda x: x['freq_2'] ** 2, axis=1)
                innerprod = df['prod'].sum()
                sqrt_1 = np.sqrt(df['sq_1'].sum())
                sqrt_2 = np.sqrt(df['sq_2'].sum())
                #dist_matrix[i][j] = innerprod / (sqrt_1 * sqrt_2)
                dist_matrix[i][j] = (innerprod / (sqrt_1 * sqrt_2)) * var_count_max.iloc[i] * var_count_min.iloc[j] # weighted with trace frequency
                dist_matrix[j][i] = dist_matrix[i][j]
        if i >= min_len:

    if len(var_list_1) >= len(var_list_2):
        dist_matrix = dist_matrix
    else:
        dist_matrix = np.transpose(dist_matrix)
    '''

    if (single):
        # print(max_freq)
        # single linkage
        dist = np.sum(max_per_var) / np.sum(max_freq)
    else:
        vmax_vec = (var_count_max.values).reshape(-1, 1)
        # print(vmax_vec)
        vmin_vec = (var_count_min.values).reshape(1, -1)
        # print(vmin_vec)
        vec_sum = np.sum(np.dot(vmax_vec, vmin_vec))
        # dist = np.sum(dist_matrix) / vec_sum
        dist = np.sum(col_sum) / vec_sum

    #print(dist_matrix)
    # print(max_per_var)
    # print(max_freq)

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

    single = parameters["single"] if "single" in parameters else False

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

    # print(len(var_count_max))
    # print(len(var_count_min))
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
                df = pd.merge(df_1, df_2, how='outer', on='var').fillna(0)
                # cosine similarity is used to calculate trace similarity
                dist_vec[j] = (pdist(np.array([df['freq_x'].values, df['freq_y'].values]), 'cosine')[0])
                # print(innerprod)
                # dist_vec[j] = innerprod / (sqrt_1 * sqrt_2)
                dist_matrix[i][j] = 1 - dist_vec[j]
                if (j == min_len - 1):
                    # dist_matrix[i][j] = (innerprod / (sqrt_1 * sqrt_2)) * var_count_max.iloc[i] * var_count_min.iloc[
                    # j]  # weighted with trace frequency

                    med_loc = np.argsort(dist_vec)[len(dist_vec) // 2]
                    max_freq[i] = var_count_max.iloc[i] * var_count_min.iloc[med_loc]
                    max_per_var[i] = dist_vec[med_loc] * max_freq[i]

                    # col_sum[i] += dist_vec[j] * var_count_max.iloc[i] * var_count_min.iloc[j]
                    # print([i,j,var_count_max.iloc[i] * var_count_min.iloc[j]])
                    # print(col_sum[i])
                    # col_sum[i] += dist_vec[j]
                    # vec_sum += var_count_max.iloc[i] * var_count_min.iloc[j]

        # single linkage
    dist = np.sum(max_per_var) / np.sum(max_freq)

    print(dist_matrix)
    # print(max_per_var)
    # print(max_freq)

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

    single = parameters["single"] if "single" in parameters else False

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

    # print(len(var_count_max))
    # print(len(var_count_min))
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
                df = pd.merge(df_1, df_2, how='outer', on='var').fillna(0)
                # cosine similarity is used to calculate trace similarity
                dist_vec[j] = (pdist(np.array([df['freq_x'].values, df['freq_y'].values]), 'cosine')[0])
                # print(innerprod)
                # dist_vec[j] = innerprod / (sqrt_1 * sqrt_2)
                dist_matrix[i][j] = dist_vec[j]
                # dist_matrix[i][j] = innerprod / (sqrt_1 * sqrt_2)
                if j == (min_len - 1):
                    # max_loc_col = np.argmax(dist_matrix[i, :])  # location of max value
                    max_loc_col = np.argmin(dist_vec)
                    if abs(dist_vec[max_loc_col]) <= 1e-6:
                        index_rec.discard(max_loc_col)
                        # print("skip:",[i,max_loc_col])
                        max_freq[i] = var_count_max.iloc[i] * var_count_min.iloc[max_loc_col] * 2
                        max_per_var[i] = dist_vec[max_loc_col] * max_freq[i] * 2
                    else:
                        max_freq[i] = var_count_max.iloc[i] * var_count_min.iloc[max_loc_col]
                        max_per_var[i] = dist_vec[max_loc_col] * max_freq[i]
                        # print(type(dist_vec)) # location of max value
                        # print([i,max_loc_col])
                        # max_per_var[i] = dist_vec[max_loc_col]
                        # max_per_var[i] = dist_matrix[i][max_loc_col] * var_count_max.iloc[i] * var_count_min.iloc[
                        #    max_loc_col]

        for i in list(index_rec):
            min_loc_row = np.argmin(dist_matrix[:, i])
            min_freq[i] = var_count_max.iloc[min_loc_row] * var_count_min.iloc[i]
            min_per_var[i] = dist_matrix[min_loc_row, i] * min_freq[i]
            # print("dual",[i,min_loc_row])
            # print("dual",dist_matrix[min_loc_row, i])

    if (single):
        # print(max_freq)
        # single linkage
        dist = (np.sum(max_per_var) + np.sum(min_per_var)) / (np.sum(max_freq) + np.sum(min_freq))
    else:
        vmax_vec = (var_count_max.values).reshape(-1, 1)
        # print(vmax_vec)
        vmin_vec = (var_count_min.values).reshape(1, -1)
        # print(vmin_vec)
        vec_sum = np.sum(np.dot(vmax_vec, vmin_vec))
        # dist = np.sum(dist_matrix) / vec_sum
        dist = np.sum(col_sum) / vec_sum

    # print(index_rec)
    # print(1-dist_matrix)
    # print(max_per_var)
    # print(max_freq)

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

    #print("list1:", max_len)
    #print("list2:", min_len)

    #print((var_count_max))
    #print((var_count_min))
    dist_matrix = np.zeros((max_len, min_len))
    max_per_var = np.zeros(max_len)
    max_freq = np.zeros(max_len)
    min_freq = np.zeros(min_len)
    min_per_var = np.zeros(min_len)
    col_sum = np.zeros(max_len)
    index_rec = set(list(range(min_len)))

    if var_list_1 == var_list_2:
        # print("Please give different variant lists!")
        dist = 0
    else:
        for i in range(max_len):
            dist_vec = np.zeros(min_len)
            df_1 = occu_var_act(max_var[i])
            for j in range(min_len):
                df_2 = occu_var_act(min_var[j])
                df = pd.merge(df_1, df_2, how='outer', on='var').fillna(0)
                #print(df)
                # cosine similarity is used to calculate trace similarity
                dist_vec[j] = (pdist(np.array([df['freq_x'].values, df['freq_y'].values]), 'cosine')[0])
                # print(innerprod)
                # dist_vec[j] = innerprod / (sqrt_1 * sqrt_2)
                dist_matrix[i][j] = dist_vec[j]
                #print(dist_vec[j])
                # dist_matrix[i][j] = innerprod / (sqrt_1 * sqrt_2)
                if j == (min_len - 1):
                    # max_loc_col = np.argmax(dist_matrix[i, :])  # location of max value
                    max_loc_col = np.argmin(dist_vec)
                    if abs(dist_vec[max_loc_col]) <= 1e-8:
                        index_rec.discard(max_loc_col)
                        #print("skip:",[i,max_loc_col])
                        max_freq[i] = var_count_max.iloc[i] * var_count_min.iloc[max_loc_col] * 2
                        max_per_var[i] = dist_vec[max_loc_col] * max_freq[i] * 2
                    else:
                        max_freq[i] = var_count_max.iloc[i] * var_count_min.iloc[max_loc_col]
                        #print("max", [i, max_loc_col])
                        max_per_var[i] = dist_vec[max_loc_col] * max_freq[i]
                        # print(type(dist_vec)) # location of max value
                        # print([i,max_loc_col])
                        # max_per_var[i] = dist_vec[max_loc_col]
                        # max_per_var[i] = dist_matrix[i][max_loc_col] * var_count_max.iloc[i] * var_count_min.iloc[
                        #    max_loc_col]

        if (len(index_rec) != 0):
            #print(index_rec)
            for i in list(index_rec):
                min_loc_row = np.argmin(dist_matrix[:, i])
                min_freq[i] = var_count_max.iloc[min_loc_row] * var_count_min.iloc[i]
                min_per_var[i] = dist_matrix[min_loc_row, i] * min_freq[i]
            # print("dual",[i,min_loc_row])
            # print("dual",dist_matrix[min_loc_row, i])

        # print(max_freq)
        # single linkage
        #print(max_freq, max_per_var)
        #print(min_freq, min_per_var)
        dist = (np.sum(max_per_var) + np.sum(min_per_var)) / (np.sum(max_freq) + np.sum(min_freq))

    # print(index_rec)
    #print(dist_matrix)
    # print(max_per_var)
    # print(max_freq)

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

    #print("list1:", max_len)
    #print("list2:", min_len)

    # print(dataframe_1)
    # print(dataframe_2)
    dist_matrix = np.zeros((max_len, min_len))
    col_sum = np.zeros(max_len)

    for i in range(max_len):
        dist_vec = np.zeros(min_len)
        df_1 = occu_var_act(max_var[i])
        for j in range(min_len):
            df_2 = occu_var_act(min_var[j])
            df = pd.merge(df_1, df_2, how='outer', on='var').fillna(0)
            #print([i,j,df])
            # cosine similarity is used to calculate trace similarity
            dist_vec[j] = (pdist(np.array([df['freq_x'].values, df['freq_y'].values]), 'cosine')[0])
            # print([i, j, df, dist_vec[j]])
            col_sum[i] += dist_vec[j] * var_count_max.iloc[i] * var_count_min.iloc[j]
            dist_matrix[i][j] = dist_vec[j]


    vmax_vec = (var_count_max.values).reshape(-1, 1)
    #print(vmax_vec)
    vmin_vec = (var_count_min.values).reshape(1, -1)
    #print(vmin_vec)
    vec_sum = np.sum(np.dot(vmax_vec, vmin_vec))
    # dist = np.sum(dist_matrix) / vec_sum
    dist = np.sum(col_sum) / vec_sum

    #print(dist_matrix)

    # print(index_rec)
    #print(dist_matrix)
    # print(max_per_var)
    # print(max_freq)

    return dist

def act_sim_percent_avg_actset(log1, log2, percent_1, percent_2,actset):
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

    #print("list1:", max_len)
    #print("list2:", min_len)

    #print((var_count_max))
    #print((var_count_min))
    dist_matrix = np.zeros((max_len, min_len))
    col_sum = np.zeros(max_len)

    for i in range(max_len):
        dist_vec = np.zeros(min_len)
        df_1 = occu_var_act(max_var[i])
        df_1 = pd.merge(actset['var'], df_1, how='outer', on='var').fillna(0)
        print("df1",df_1)
        for j in range(min_len):
            df_2 = occu_var_act(min_var[j])
            df = pd.merge(df_1, df_2, how='outer', on='var').fillna(0)
            print([i,j,df])
            # cosine similarity is used to calculate trace similarity
            dist_vec[j] = (pdist(np.array([df['freq_x'].values, df['freq_y'].values]), 'cosine')[0])
            col_sum[i] += dist_vec[j] * var_count_max.iloc[i] * var_count_min.iloc[j]
            dist_matrix[i][j] = dist_vec[j]


    vmax_vec = (var_count_max.values).reshape(-1, 1)
    #print(vmax_vec)
    vmin_vec = (var_count_min.values).reshape(1, -1)
    #print(vmin_vec)
    vec_sum = np.sum(np.dot(vmax_vec, vmin_vec))
    # dist = np.sum(dist_matrix) / vec_sum
    dist = np.sum(col_sum) / vec_sum

    #print(dist_matrix)

    # print(index_rec)
    #print(dist_matrix)
    # print(max_per_var)
    # print(max_freq)

    return dist
