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
from pm4py.objects.conversion.log import converter as log_converter
from pm4py.algo.transformation.log_to_features import algorithm as features_extractor
from enum import Enum
from pm4py.util import exec_utils
from pm4py.objects.log.obj import EventLog, EventStream
import pandas as pd
import numpy as np
from typing import Optional, Dict, Any, Generator, Union
from copy import copy


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

    from pm4py.util import ml_utils
    clusterer = exec_utils.get_param_value(Parameters.SKLEARN_CLUSTERER, parameters, ml_utils.KMeans(n_clusters=2, random_state=0, n_init="auto"))

    if "enable_activity_def_representation" not in parameters:
        parameters["enable_activity_def_representation"] = True

    if "enable_succ_def_representation" not in parameters:
        parameters["enable_succ_def_representation"] = True

    conv_parameters = copy(parameters)
    conv_parameters["stream_postprocessing"] = True

    log = log_converter.apply(log, variant=log_converter.Variants.TO_EVENT_LOG, parameters=conv_parameters)
    data, feature_names = features_extractor.apply(log, parameters=parameters)
    data = np.array([np.array(x) for x in data])

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
