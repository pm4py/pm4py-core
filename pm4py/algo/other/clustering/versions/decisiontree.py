from copy import copy

from pm4py.objects.log.util import get_log_representation
from sklearn.decomposition import PCA
from sklearn.cluster import DBSCAN
from pm4py.objects.log.log import EventLog, Trace


def apply(log, parameters=None):
    """
    Apply PCA + DBSCAN clustering after creating a representation of the log containing
    the wanted attributes and the wanted succession of attributes

    Parameters
    -----------
    log
        Trace log
    parameters
        Parameters of the algorithm, including:
            pca_components -> Number of the components for the PCA
            dbscan_eps -> EPS value for the DBScan clustering
            str_tr_attr -> String trace attributes to consider in feature representation
            str_ev_attr -> String event attributes to consider in feature representation
            num_tr_attr -> Numeric trace attributes to consider in feature representation
            num_ev_attr -> Numeric event attributes to consider in feature representation
            str_evsucc_attr -> Succession between event attributes to consider in feature representation

    Returns
    -----------
    log_list
        A list containing, for each cluster, a different log
    """
    if parameters is None:
        parameters = {}

    pca_components = parameters["pca_components"] if "pca_components" in parameters else 3
    dbscan_eps = parameters["dbscan_eps"] if "dbscan_eps" in parameters else 0.3

    log_list = []

    str_tr_attr = parameters["str_tr_attr"] if "str_tr_attr" in parameters else copy([])
    str_ev_attr = parameters["str_ev_attr"] if "str_ev_attr" in parameters else copy(["concept:name"])
    num_tr_attr = parameters["num_tr_attr"] if "num_tr_attr" in parameters else copy([])
    num_ev_attr = parameters["num_ev_attr"] if "num_ev_attr" in parameters else copy([])
    str_evsucc_attr = parameters["str_evsucc_attr"] if "str_evsucc_attr" in parameters else copy(["concept:name"])

    data, feature_names = get_log_representation.get_representation(log, str_tr_attr, str_ev_attr, num_tr_attr,
                                                                    num_ev_attr, str_evsucc_attr=str_evsucc_attr)

    pca = PCA(n_components=pca_components)
    pca.fit(data)
    data2d = pca.transform(data)

    db = DBSCAN(eps=dbscan_eps).fit(data2d)
    labels = db.labels_

    already_seen = {}

    for i in range(len(log)):
        if not labels[i] in already_seen:
            already_seen[labels[i]] = len(list(already_seen.keys()))
            log_list.append(EventLog())
        trace = Trace(log[i])
        log_list[already_seen[labels[i]]].append(trace)

    return log_list
