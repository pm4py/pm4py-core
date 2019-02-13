from datetime import datetime

import numpy as np
from sklearn.cluster import Birch
from sklearn.decomposition import PCA

from pm4py.algo.other.decisiontree import get_log_representation
from pm4py.objects.log.log import EventLog, Trace
from pm4py.objects.log.util import sorting
from pm4py.objects.log.util import xes
from pm4py.util import constants

from pm4py.objects.conversion.log import factory as conversion_factory


def apply(log, parameters=None):
    """
    Apply PCA + Birch clustering, taking into account the control flow perspective but also the other perspectives,
    in order to possibly detect concept drift

    Parameters
    -------------
    log
        Log
    parameters
        Possible parameters of the algorithm:

    """
    if parameters is None:
        parameters = {}

    pca_components = parameters["pca_components"] if "pca_components" in parameters else 6
    min_rel_size_cluster = parameters["min_rel_size_cluster"] if "min_rel_size_cluster" in parameters else 0.05

    timestamp_key = parameters[
        constants.PARAMETER_CONSTANT_TIMESTAMP_KEY] if constants.PARAMETER_CONSTANT_TIMESTAMP_KEY in parameters else xes.DEFAULT_TIMESTAMP_KEY

    log = sorting.sort_timestamp(log, timestamp_key=timestamp_key)
    data, feature_names = get_log_representation.get_default_representation(log)

    start_end_timestamp = np.zeros((len(log), 2))

    min_timestamp = (log[0][0][timestamp_key].replace(tzinfo=None) - datetime(1970, 1, 1)).total_seconds()
    # last timestamp is not necessarily the maximum
    last_timestamp_diff_min = (log[-1][-1][timestamp_key].replace(tzinfo=None) - datetime(1970, 1,
                                                                                          1)).total_seconds() - min_timestamp

    for index, trace in enumerate(log):
        start_end_timestamp[index, 0] = 2 * (((trace[0][timestamp_key].replace(tzinfo=None) - datetime(1970, 1,
                                                                                                       1)).total_seconds() - min_timestamp) / last_timestamp_diff_min) - 1
        start_end_timestamp[index, 1] = 2 * (((trace[-1][timestamp_key].replace(tzinfo=None) - datetime(1970, 1,
                                                                                                        1)).total_seconds() - min_timestamp) / last_timestamp_diff_min) - 1

    pca = PCA(n_components=pca_components)
    pca.fit(data)
    data2d = pca.transform(data)

    data2d = np.hstack((data2d, start_end_timestamp))

    for cluster_size in range(2,5+1):
        db = Birch(n_clusters=cluster_size).fit(data2d)
        labels = db.labels_

        logs_list = []
        already_seen = {}

        for i in range(len(log)):
            if not labels[i] in already_seen:
                already_seen[labels[i]] = len(list(already_seen.keys()))
                logs_list.append(EventLog())
            trace = Trace(log[i])
            logs_list[already_seen[labels[i]]].append(trace)

        logs_list = [x for x in logs_list if len(x) > min_rel_size_cluster * len(log)]
        event_streams_list = [sorted(conversion_factory.apply(x, variant=conversion_factory.TO_EVENT_STREAM), key=lambda y: (y[timestamp_key].replace(tzinfo=None) - datetime(1970, 1, 1)).total_seconds()) for x in logs_list]
        del logs_list

        event_streams_list = sorted(event_streams_list, key=lambda x: x[int(0.5*len(x))][timestamp_key])

        i = 0
        while i < len(event_streams_list)-1:
            first_quart_i = (event_streams_list[i][int(len(event_streams_list[i])*0.25)][timestamp_key].replace(tzinfo=None) - datetime(1970, 1, 1)).total_seconds()
            third_quart_i = (event_streams_list[i][int(len(event_streams_list[i])*0.75)][timestamp_key].replace(tzinfo=None) - datetime(1970, 1, 1)).total_seconds()
            first_quart_i1 = (event_streams_list[i+1][int(len(event_streams_list[i+1])*0.25)][timestamp_key].replace(tzinfo=None) - datetime(1970, 1, 1)).total_seconds()
            third_quart_i1 = (event_streams_list[i+1][int(len(event_streams_list[i+1])*0.75)][timestamp_key].replace(tzinfo=None) - datetime(1970, 1, 1)).total_seconds()

            if third_quart_i > first_quart_i1:
                event_streams_list[i] = event_streams_list[i] + event_streams_list[i+1]
                event_streams_list[i] = sorted(event_streams_list[i], key=lambda y: (y[timestamp_key].replace(tzinfo=None) - datetime(1970, 1, 1)).total_seconds())
                event_streams_list = sorted(event_streams_list,
                                          key=lambda y: (y[int(len(y)*0.5)][timestamp_key].replace(tzinfo=None) - datetime(1970, 1,
                                                                                                          1)).total_seconds())

                del event_streams_list[i+1]
                continue
            i = i + 1

        logs_list = [conversion_factory.apply(x) for x in event_streams_list]

        if len(logs_list) > 1:
            return logs_list

    return logs_list
