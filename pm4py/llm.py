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
from pm4py.objects.log.obj import EventLog, EventStream, Trace
from typing import Union, Optional, Dict, Tuple
from pm4py.utils import get_properties, constants
from pm4py.utils import __event_log_deprecation_warning
from pm4py.objects.ocel.obj import OCEL
from pm4py.objects.petri_net.obj import PetriNet, Marking


def openai_query(prompt: str, api_key: Optional[str] = None, openai_model: Optional[str] = None) -> str:
    """
    Executes the provided prompt, obtaining the answer from the OpenAI APIs.

    :param prompt: prompt that should be executed
    :param api_key: OpenAI API key
    :param openai_model: OpenAI model to be used (default: gpt-3.5-turbo)
    :rtype: ``str``

    .. code-block:: python3

        import pm4py

        resp = pm4py.llm.openai_query('what is the result of 3+3?', api_key="sk-382393", openai_model="gpt-3.5-turbo")
        print(resp)
    """
    parameters = {}
    if api_key is not None:
        parameters["api_key"] = api_key
    if openai_model is not None:
        parameters["openai_model"] = openai_model

    from pm4py.algo.querying.llm.connectors import openai as perform_query
    return perform_query.apply(prompt, parameters=parameters)


def abstract_dfg(log_obj: Union[pd.DataFrame, EventLog, EventStream], max_len: int = constants.OPENAI_MAX_LEN, include_performance: bool = True, relative_frequency: bool = False, response_header: bool = True, primary_performance_aggregation: str = "mean", secondary_performance_aggregation: Optional[str] = None, activity_key: str = "concept:name", timestamp_key: str = "time:timestamp", case_id_key: str = "case:concept:name") -> str:
    """
    Obtains the DFG abstraction of a traditional event log

    :param log_obj: log object
    :param max_len: maximum length of the (string) abstraction
    :param include_performance: (boolean) includes the performance of the paths in the abstraction
    :param relative_frequency: (boolean) uses the relative instead of the absolute frequency of the paths
    :param response_header: includes a short header before the paths, pointing to the description of the abstraction
    :param primary_performance_aggregation: primary aggregation to be used for the arc's performance (default: mean, other options: median, min, max, sum, stdev)
    :param secondary_performance_aggregation: (optional) secondary aggregation to be used for the arc's performance (default None, other options: mean, median, min, max, sum, stdev)
    :param activity_key: the column to be used as activity
    :param timestamp_key: the column to be used as timestamp
    :param case_id_key: the column to be used as case identifier
    :rtype: ``str``

    .. code-block:: python3

        import pm4py

        log = pm4py.read_xes("tests/input_data/roadtraffic100traces.xes")
        print(pm4py.llm.abstract_dfg(log))
    """
    __event_log_deprecation_warning(log_obj)

    parameters = get_properties(
        log_obj, activity_key=activity_key, timestamp_key=timestamp_key, case_id_key=case_id_key)
    parameters["max_len"] = max_len
    parameters["include_performance"] = include_performance
    parameters["relative_frequency"] = relative_frequency
    parameters["response_header"] = response_header
    parameters["primary_performance_aggregation"] = primary_performance_aggregation
    parameters["secondary_performance_aggregation"] = secondary_performance_aggregation

    from pm4py.algo.querying.llm.abstractions import log_to_dfg_descr
    return log_to_dfg_descr.apply(log_obj, parameters=parameters)


def abstract_variants(log_obj: Union[pd.DataFrame, EventLog, EventStream], max_len: int = constants.OPENAI_MAX_LEN, include_performance: bool = True, relative_frequency: bool = False, response_header: bool = True, primary_performance_aggregation: str = "mean", secondary_performance_aggregation: Optional[str] = None,  activity_key: str = "concept:name", timestamp_key: str = "time:timestamp", case_id_key: str = "case:concept:name") -> str:
    """
    Obtains the variants abstraction of a traditional event log

    :param log_obj: log object
    :param max_len: maximum length of the (string) abstraction
    :param include_performance: (boolean) includes the performance of the variants in the abstraction
    :param relative_frequency: (boolean) uses the relative instead of the absolute frequency of the variants
    :param response_header: includes a short header before the variants, pointing to the description of the abstraction
    :param primary_performance_aggregation: primary aggregation to be used for the arc's performance (default: mean, other options: median, min, max, sum, stdev)
    :param secondary_performance_aggregation: (optional) secondary aggregation to be used for the arc's performance (default None, other options: mean, median, min, max, sum, stdev)
    :param activity_key: the column to be used as activity
    :param timestamp_key: the column to be used as timestamp
    :param case_id_key: the column to be used as case identifier
    :rtype: ``str``

    .. code-block:: python3

        import pm4py

        log = pm4py.read_xes("tests/input_data/roadtraffic100traces.xes")
        print(pm4py.llm.abstract_variants(log))
    """
    __event_log_deprecation_warning(log_obj)

    parameters = get_properties(
        log_obj, activity_key=activity_key, timestamp_key=timestamp_key, case_id_key=case_id_key)
    parameters["max_len"] = max_len
    parameters["include_performance"] = include_performance
    parameters["relative_frequency"] = relative_frequency
    parameters["response_header"] = response_header
    parameters["primary_performance_aggregation"] = primary_performance_aggregation
    parameters["secondary_performance_aggregation"] = secondary_performance_aggregation

    from pm4py.algo.querying.llm.abstractions import log_to_variants_descr
    return log_to_variants_descr.apply(log_obj, parameters=parameters)


def abstract_ocel(ocel: OCEL, include_timestamps: bool = True) -> str:
    """
    Obtains the abstraction of an object-centric event log, including the list of events and the objects of the OCEL

    :param ocel: object-centric event log
    :param include_timestamps: (boolean) includes the timestamp information in the abstraction
    :rtype: ``str``

    .. code-block:: python3

        import pm4py

        ocel = pm4py.read_ocel("tests/input_data/ocel/example_log.jsonocel")
        print(pm4py.llm.abstract_ocel(ocel))
    """
    parameters = {}
    parameters["include_timestamps"] = include_timestamps

    from pm4py.algo.transformation.ocel.description import algorithm as ocel_description
    return ocel_description.apply(ocel, parameters=parameters)


def abstract_ocel_ocdfg(ocel: OCEL, include_header: bool = True, include_timestamps: bool = True, max_len: int = constants.OPENAI_MAX_LEN) -> str:
    """
    Obtains the abstraction of an object-centric event log, representing in text the object-centric directly-follows
    graph

    :param ocel: object-centric event log
    :param include_header: (boolean) includes the header in the abstraction
    :param include_timestamps: (boolean) includes the timestamp information in the abstraction
    :param max_len: maximum length of the abstraction
    :rtype: ``str``

    .. code-block:: python3

        import pm4py

        ocel = pm4py.read_ocel("tests/input_data/ocel/example_log.jsonocel")
        print(pm4py.llm.abstract_ocel_ocdfg(ocel))
    """
    parameters = {}
    parameters["include_header"] = include_header
    parameters["include_timestamps"] = include_timestamps
    parameters["max_len"] = max_len

    from pm4py.algo.querying.llm.abstractions import ocel_ocdfg_descr
    return ocel_ocdfg_descr.apply(ocel, parameters=parameters)


def abstract_ocel_features(ocel: OCEL, obj_type: str, include_header: bool = True, max_len: int = constants.OPENAI_MAX_LEN, debug: bool = False, enable_object_lifecycle_paths: bool = True) -> str:
    """
    Obtains the abstraction of an object-centric event log, representing in text the features and their values.

    :param ocel: object-centric event log
    :param obj_type: the object type that should be considered in the feature extraction
    :param include_header: (boolean) includes the header in the abstraction
    :param max_len: maximum length of the abstraction
    :param debug: enables debugging mode (telling at which point of the feature extraction you are)
    :param enable_object_lifecycle_paths: enables the "lifecycle paths" feature
    :rtype: ``str``

    .. code-block:: python3

        import pm4py

        ocel = pm4py.read_ocel("tests/input_data/ocel/example_log.jsonocel")
        print(pm4py.llm.abstract_ocel_ocdfg(ocel))
    """
    parameters = {}
    parameters["include_header"] = include_header
    parameters["max_len"] = max_len
    parameters["debug"] = debug
    parameters["enable_object_lifecycle_paths"] = enable_object_lifecycle_paths

    from pm4py.algo.querying.llm.abstractions import ocel_fea_descr
    return ocel_fea_descr.apply(ocel, obj_type, parameters=parameters)


def abstract_event_stream(log_obj: Union[pd.DataFrame, EventLog, EventStream], max_len: int = constants.OPENAI_MAX_LEN, response_header: bool = True, activity_key: str = "concept:name", timestamp_key: str = "time:timestamp", case_id_key: str = "case:concept:name") -> str:
    """
    Obtains the event stream abstraction of a traditional event log

    :param log_obj: log object
    :param max_len: maximum length of the (string) abstraction
    :param response_header: includes a short header before the variants, pointing to the description of the abstraction
    :param activity_key: the column to be used as activity
    :param timestamp_key: the column to be used as timestamp
    :param case_id_key: the column to be used as case identifier
    :rtype: ``str``

    .. code-block:: python3

        import pm4py

        log = pm4py.read_xes("tests/input_data/roadtraffic100traces.xes")
        print(pm4py.llm.abstract_event_stream(log))
    """
    __event_log_deprecation_warning(log_obj)

    parameters = get_properties(
        log_obj, activity_key=activity_key, timestamp_key=timestamp_key, case_id_key=case_id_key)
    parameters["max_len"] = max_len
    parameters["response_header"] = response_header

    from pm4py.algo.querying.llm.abstractions import stream_to_descr
    return stream_to_descr.apply(log_obj, parameters=parameters)


def abstract_petri_net(net: PetriNet, im: Marking, fm: Marking, response_header: bool = True) -> str:
    """
    Obtain an abstraction of a Petri net

    :param net: Petri net
    :param im: Initial marking
    :param fm: Final marking
    :param response_header: includes the header of the response
    :rtype: ``str``

    .. code-block:: python3

        import pm4py

        net, im, fm = pm4py.read_pnml('tests/input_data/running-example.pnml')
        print(pm4py.llm.abstract_petri_net(net, im, fm))
    """
    parameters = {}
    parameters["response_header"] = response_header

    from pm4py.algo.querying.llm.abstractions import net_to_descr
    return net_to_descr.apply(net, im, fm, parameters=parameters)


def abstract_log_attributes(log_obj: Union[pd.DataFrame, EventLog, EventStream], max_len: int = constants.OPENAI_MAX_LEN, activity_key: str = "concept:name", timestamp_key: str = "time:timestamp", case_id_key: str = "case:concept:name") -> str:
    """
    Abstracts the attributes of a log (reporting their name, their type, and the top values)

    :param log_obj: log object
    :param max_len: maximum length of the (string) abstraction
    :param activity_key: the column to be used as activity
    :param timestamp_key: the column to be used as timestamp
    :param case_id_key: the column to be used as case identifier
    :rtype: ``str``

    .. code-block:: python3

        import pm4py

        log = pm4py.read_xes("tests/input_data/roadtraffic100traces.xes")
        print(pm4py.llm.abstract_log_attributes(log))
    """
    __event_log_deprecation_warning(log_obj)

    parameters = get_properties(
        log_obj, activity_key=activity_key, timestamp_key=timestamp_key, case_id_key=case_id_key)
    parameters["max_len"] = max_len

    from pm4py.algo.querying.llm.abstractions import log_to_cols_descr
    return log_to_cols_descr.apply(log_obj, parameters=parameters)


def abstract_log_features(log_obj: Union[pd.DataFrame, EventLog, EventStream], max_len: int = constants.OPENAI_MAX_LEN, include_header: bool = True, activity_key: str = "concept:name", timestamp_key: str = "time:timestamp", case_id_key: str = "case:concept:name") -> str:
    """
    Abstracts the machine learning features obtained from a log (reporting the top features until the desired length is obtained)

    :param log_obj: log object
    :param max_len: maximum length of the (string) abstraction
    :param activity_key: the column to be used as activity
    :param timestamp_key: the column to be used as timestamp
    :param case_id_key: the column to be used as case identifier
    :rtype: ``str``

    .. code-block:: python3

        import pm4py

        log = pm4py.read_xes("tests/input_data/roadtraffic100traces.xes")
        print(pm4py.llm.abstract_log_features(log))
    """
    __event_log_deprecation_warning(log_obj)

    parameters = get_properties(
        log_obj, activity_key=activity_key, timestamp_key=timestamp_key, case_id_key=case_id_key)
    parameters["max_len"] = max_len
    parameters["include_header"] = include_header

    from pm4py.algo.querying.llm.abstractions import log_to_fea_descr
    return log_to_fea_descr.apply(log_obj, parameters=parameters)


def abstract_temporal_profile(temporal_profile: Dict[Tuple[str, str], Tuple[float, float]], include_header: bool = True) -> str:
    """
    Abstracts a temporal profile model to a string.

    :param temporal_profile: temporal profile model
    :param include_header: includes an header in the response, describing the temporal profile
    :rtype: ``str``

    .. code-block:: python3

        import pm4py

        log = pm4py.read_xes("tests/input_data/roadtraffic100traces.xes", return_legacy_log_object=True)
        temporal_profile = pm4py.discover_temporal_profile(log)
        text_abstr = pm4py.llm.abstract_temporal_profile(temporal_profile, include_header=True)
        print(text_abstr)
    """
    parameters = {}
    parameters["include_header"] = include_header

    from pm4py.algo.querying.llm.abstractions import tempprofile_to_descr
    return tempprofile_to_descr.apply(temporal_profile, parameters=parameters)


def abstract_case(case: Trace, include_case_attributes: bool = True, include_event_attributes: bool = True, include_timestamp: bool = True, include_header: bool = True, activity_key: str = "concept:name", timestamp_key: str = "time:timestamp") -> str:
    """
    Textually abstracts a case

    :param case: case object
    :param include_case_attributes: (boolean) include or not the attributes at the case level
    :param include_event_attributes: (boolean) include or not the attributes at the event level
    :param include_timestamp: (boolean) include or not the event timestamp in the abstraction
    :param include_header: (boolean) includes the header of the response
    :param activity_key: the column to be used as activity
    :param timestamp_key: the column to be used as timestamp
    :rtype: ``str``

    .. code-block:: python3

        import pm4py

        log = pm4py.read_xes("tests/input_data/roadtraffic100traces.xes", return_legacy_log_object=True)
        print(pm4py.llm.abstract_case(log[0]))
    """
    parameters = {}
    parameters["include_case_attributes"] = include_case_attributes
    parameters["include_event_attributes"] = include_event_attributes
    parameters["include_timestamp"] = include_timestamp
    parameters["include_header"] = include_header
    parameters[constants.PARAMETER_CONSTANT_ACTIVITY_KEY] = activity_key
    parameters[constants.PARAMETER_CONSTANT_TIMESTAMP_KEY] = timestamp_key

    from pm4py.algo.querying.llm.abstractions import case_to_descr
    return case_to_descr.apply(case, parameters=parameters)


def abstract_declare(declare_model, include_header: bool = True) -> str:
    """
    Textually abstracts a DECLARE model

    :param declare: DECLARE model
    :param include_header: (boolean) includes the header of the response
    :rtype: ``str``

    .. code-block:: python3

        import pm4py

        log = pm4py.read_xes("tests/input_data/roadtraffic100traces.xes", return_legacy_log_object=True)
        log_ske = pm4py.discover_declare(log)
        print(pm4py.llm.abstract_declare(log_ske))
    """
    parameters = {}
    parameters["include_header"] = include_header

    from pm4py.algo.querying.llm.abstractions import declare_to_descr
    return declare_to_descr.apply(declare_model, parameters=parameters)


def abstract_log_skeleton(log_skeleton, include_header: bool = True) -> str:
    """
    Textually abstracts a log skeleton process model

    :param log_skeleton: log skeleton
    :param include_header: (boolean) includes the header of the response
    :rtype: ``str``

    .. code-block:: python3

        import pm4py

        log = pm4py.read_xes("tests/input_data/roadtraffic100traces.xes", return_legacy_log_object=True)
        log_ske = pm4py.discover_log_skeleton(log)
        print(pm4py.llm.abstract_log_skeleton(log_ske))
    """
    parameters = {}
    parameters["include_header"] = include_header

    from pm4py.algo.querying.llm.abstractions import logske_to_descr
    return logske_to_descr.apply(log_skeleton, parameters=parameters)
