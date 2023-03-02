from pm4py.objects.conversion.log import converter as log_converter
from pm4py.algo.transformation.log_to_features import algorithm as features_extractor
from enum import Enum
from pm4py.util import exec_utils
from pm4py.objects.log.obj import EventLog, EventStream
import pandas as pd
from typing import Optional, Dict, Any, Generator, Union


class Parameters(Enum):
    SKLEARN_CLUSTERER = "sklearn_clusterer"


def apply(log: Union[EventLog, EventStream, pd.DataFrame], parameters: Optional[Dict[Any, Any]] = None) -> Generator[EventLog, None, None]:
    """
    Cluster the event log, based on the extraction of profiles for the traces of the event log
    (by means of the feature extraction proposed in pm4py) and the application of a Scikit learn clusterer
    (default: K-means with two clusters)

    Implements the approach described in:
    Song, Minseok, Christian W. Günther, and Wil MP Van der Aalst. "Trace clustering in process mining." Business Process Management Workshops: BPM 2008 International Workshops, Milano, Italy, September 1-4, 2008. Revised Papers 6. Springer Berlin Heidelberg, 2009.

    Parameters
    ----------------
    log
        Event log
    parameters
        Parameters of the feature extraction, including:
        - Parameters.SKLEARN_CLUSTERER => the Scikit-Learn clusterer to be used (default: KMeans(n_clusters=2, random_state=0, n_init="auto"))

    Returns
    ---------------
    generator
        Generator of logs (clusters)
    """
    if parameters is None:
        parameters = {}

    from sklearn.cluster import KMeans
    clusterer = exec_utils.get_param_value(Parameters.SKLEARN_CLUSTERER, parameters, KMeans(n_clusters=2, random_state=0, n_init="auto"))

    parameters["enable_activity_def_representation"] = True
    parameters["enable_succ_def_representation"] = True

    log = log_converter.apply(log, variant=log_converter.Variants.TO_EVENT_LOG, parameters=parameters)
    data, feature_names = features_extractor.apply(log, parameters=parameters)

    clusters = clusterer.fit_predict(data)
    max_clu = max(clusters)
    clust_idxs = {i: list() for i in range(max_clu+1)}

    for i in range(len(clusters)):
        clust_idxs[clusters[i]].append(i)

    for i in clust_idxs:
        clust_log = EventLog()
        for j in clust_idxs[i]:
            clust_log.append(log[j])
        #clust_log = log_converter.apply(clust_log, variant=log_converter.Variants.TO_DATA_FRAME, parameters=parameters)

        yield clust_log
