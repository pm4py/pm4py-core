from datetime import datetime

import numpy as np
from sklearn.cluster import Birch
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score

from pm4py.objects.conversion.log import factory as conversion_factory
from pm4py.objects.log.log import EventLog, Trace, EventStream
from pm4py.objects.log.util import sorting, get_log_representation
from pm4py.objects.log.util import xes
from pm4py.util import constants


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
            pca_components -> Number of components to consider in the PCA
            min_rel_size_cluster -> Remove clusters that are smaller in size than this amount in comparison to the log
            min_n_clusters_to_search -> Provides the minimum number of clusters to search by the algorithm
            max_n_clusters_to_search -> Provides the maximum number of clusters to search by the algorithm
            enable_succattr -> Enables the usage of activity succession order in order to build the log representation

    Returns
    ------------
    a list containing:
        boolean
            A boolean indicating if the concept drift was correctly detected
        logs_list
            List of event logs
        endpoints
            Interesting time points of the concept drift between two successive logs (e.g. third quartile of log
            at index i and first quartile of log at index i+1)
        change_date_repr
            A single date representing an estimation of when the concept drift actually happened
    """
    if parameters is None:
        parameters = {}

    pca_components = parameters["pca_components"] if "pca_components" in parameters else 6
    min_rel_size_cluster = parameters["min_rel_size_cluster"] if "min_rel_size_cluster" in parameters else 0.05
    min_n_clusters_to_search = parameters["min_n_clusters_to_search"] if "min_n_clusters_to_search" in parameters else 2
    max_n_clusters_to_search = parameters["max_n_clusters_to_search"] if "max_n_clusters_to_search" in parameters else 5
    enable_succattr = parameters["enable_succattr"] if "enable_succattr" in parameters else False

    timestamp_key = parameters[
        constants.PARAMETER_CONSTANT_TIMESTAMP_KEY] if constants.PARAMETER_CONSTANT_TIMESTAMP_KEY in parameters else xes.DEFAULT_TIMESTAMP_KEY

    log = sorting.sort_timestamp(log, timestamp_key=timestamp_key)
    data, feature_names = get_log_representation.get_default_representation(log, enable_succattr=enable_succattr)

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

    possible_outputs = []

    for cluster_size in range(min_n_clusters_to_search, max_n_clusters_to_search + 1):
        db = Birch(n_clusters=cluster_size).fit(data2d)
        labels = db.labels_

        silh_score = silhouette_score(data2d, labels)

        logs_list = []
        already_seen = {}

        for i in range(len(log)):
            if not labels[i] in already_seen:
                already_seen[labels[i]] = len(list(already_seen.keys()))
                logs_list.append(EventLog())
            trace = Trace(log[i])
            logs_list[already_seen[labels[i]]].append(trace)

        logs_list = [x for x in logs_list if len(x) > min_rel_size_cluster * len(log)]
        event_streams_list = [sorted(conversion_factory.apply(x, variant=conversion_factory.TO_EVENT_STREAM),
                                     key=lambda y: (y[timestamp_key].replace(tzinfo=None) - datetime(1970, 1,
                                                                                                     1)).total_seconds())
                              for x in logs_list]
        del logs_list

        event_streams_list = sorted(event_streams_list, key=lambda x: x[int(0.5 * len(x))][timestamp_key])

        i = 0
        while i < len(event_streams_list) - 1:
            third_quart_i = (event_streams_list[i][int(len(event_streams_list[i]) * 0.75)][timestamp_key].replace(
                tzinfo=None) - datetime(1970, 1, 1)).total_seconds()
            first_quart_i1 = (
                    event_streams_list[i + 1][int(len(event_streams_list[i + 1]) * 0.25)][timestamp_key].replace(
                        tzinfo=None) - datetime(1970, 1, 1)).total_seconds()

            if third_quart_i > first_quart_i1:
                event_streams_list[i] = event_streams_list[i] + event_streams_list[i + 1]
                event_streams_list[i] = sorted(event_streams_list[i], key=lambda y: (
                        y[timestamp_key].replace(tzinfo=None) - datetime(1970, 1, 1)).total_seconds())
                event_streams_list = sorted(event_streams_list,
                                            key=lambda y: (y[int(len(y) * 0.5)][timestamp_key].replace(
                                                tzinfo=None) - datetime(1970, 1,
                                                                        1)).total_seconds())

                del event_streams_list[i + 1]
                continue
            i = i + 1

        if len(event_streams_list) > 1:
            endpoints = []
            change_date_repr = []
            i = 0

            while i < len(event_streams_list) - 1:
                third_quart_i = (event_streams_list[i][int(len(event_streams_list[i]) * 0.75)][timestamp_key].replace(
                    tzinfo=None) - datetime(1970, 1, 1)).total_seconds()
                first_quart_i1 = (event_streams_list[i + 1][int(len(event_streams_list[i + 1]) * 0.25)][
                                      timestamp_key].replace(tzinfo=None) - datetime(1970, 1, 1)).total_seconds()

                endpoints.append((datetime.utcfromtimestamp(third_quart_i).strftime('%Y-%m-%d %H:%M:%S'),
                                  datetime.utcfromtimestamp(first_quart_i1).strftime('%Y-%m-%d %H:%M:%S')))

                intermediate_point = (third_quart_i + first_quart_i1) / 2.0
                change_date_repr.append(datetime.utcfromtimestamp(intermediate_point).strftime('%Y-%m-%d %H:%M:%S'))

                i = i + 1

            logs_list = [conversion_factory.apply(EventStream(x), variant=conversion_factory.TO_EVENT_LOG) for x in event_streams_list]

            possible_outputs.append(([True, logs_list, endpoints, change_date_repr], cluster_size, silh_score))

    possible_outputs = sorted(possible_outputs, key=lambda x: x[-1], reverse=True)

    if possible_outputs:
        return possible_outputs[0][0]

    return [False, [], [], ""]
