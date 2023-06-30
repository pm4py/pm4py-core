import pandas as pd
from pm4py.objects.log.obj import EventLog, EventStream
from typing import Union, Optional
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


def abstract_dfg(log_obj: Union[pd.DataFrame, EventLog, EventStream], max_len: int = constants.OPENAI_MAX_LEN, include_performance: bool = True, relative_frequency: bool = False, response_header: bool = True, activity_key: str = "concept:name", timestamp_key: str = "time:timestamp", case_id_key: str = "case:concept:name") -> str:
    """
    Obtains the DFG abstraction of a traditional event log

    :param log_obj: log object
    :param max_len: maximum length of the (string) abstraction
    :param include_performance: (boolean) includes the performance of the paths in the abstraction
    :param relative_frequency: (boolean) uses the relative instead of the absolute frequency of the paths
    :param response_header: includes a short header before the paths, pointing to the description of the abstraction
    :param activity_key: the column to be used as activity
    :param timestamp_key: the column to be used as timestamp
    :param case_id_key: the column to be used as case identifier
    :rtype: ``str``

    .. code-block:: python3

        import pm4py

        log = pm4py.read_xes("tests/input_data/roadtraffic100traces.xes")
        print(pm4py.llm.abstract_dfg(log))
    """
    if type(log_obj) not in [pd.DataFrame, EventLog, EventStream]: raise Exception("the method can be applied only to a traditional event log!")
    __event_log_deprecation_warning(log_obj)

    parameters = get_properties(
        log_obj, activity_key=activity_key, timestamp_key=timestamp_key, case_id_key=case_id_key)
    parameters["max_len"] = max_len
    parameters["include_performance"] = include_performance
    parameters["relative_frequency"] = relative_frequency
    parameters["response_header"] = response_header

    from pm4py.algo.querying.llm.abstractions import log_to_dfg_descr
    return log_to_dfg_descr.apply(log_obj, parameters=parameters)


def abstract_variants(log_obj: Union[pd.DataFrame, EventLog, EventStream], max_len: int = constants.OPENAI_MAX_LEN, include_performance: bool = True, relative_frequency: bool = False, response_header: bool = True, activity_key: str = "concept:name", timestamp_key: str = "time:timestamp", case_id_key: str = "case:concept:name") -> str:
    """
    Obtains the variants abstraction of a traditional event log

    :param log_obj: log object
    :param max_len: maximum length of the (string) abstraction
    :param include_performance: (boolean) includes the performance of the variants in the abstraction
    :param relative_frequency: (boolean) uses the relative instead of the absolute frequency of the variants
    :param response_header: includes a short header before the variants, pointing to the description of the abstraction
    :param activity_key: the column to be used as activity
    :param timestamp_key: the column to be used as timestamp
    :param case_id_key: the column to be used as case identifier
    :rtype: ``str``

    .. code-block:: python3

        import pm4py

        log = pm4py.read_xes("tests/input_data/roadtraffic100traces.xes")
        print(pm4py.llm.abstract_variants(log))
    """
    if type(log_obj) not in [pd.DataFrame, EventLog, EventStream]: raise Exception("the method can be applied only to a traditional event log!")
    __event_log_deprecation_warning(log_obj)

    parameters = get_properties(
        log_obj, activity_key=activity_key, timestamp_key=timestamp_key, case_id_key=case_id_key)
    parameters["max_len"] = max_len
    parameters["include_performance"] = include_performance
    parameters["relative_frequency"] = relative_frequency
    parameters["response_header"] = response_header

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


def abstract_ocel_features(ocel: OCEL, obj_type: str, include_header: bool = True, max_len: int = constants.OPENAI_MAX_LEN) -> str:
    """
    Obtains the abstraction of an object-centric event log, representing in text the features and their values.

    :param ocel: object-centric event log
    :param obj_type: the object type that should be considered in the feature extraction
    :param include_header: (boolean) includes the header in the abstraction
    :param max_len: maximum length of the abstraction
    :rtype: ``str``

    .. code-block:: python3

        import pm4py

        ocel = pm4py.read_ocel("tests/input_data/ocel/example_log.jsonocel")
        print(pm4py.llm.abstract_ocel_ocdfg(ocel))
    """
    parameters = {}
    parameters["include_header"] = include_header
    parameters["max_len"] = max_len

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
    if type(log_obj) not in [pd.DataFrame, EventLog, EventStream]: raise Exception("the method can be applied only to a traditional event log!")
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
    if type(log_obj) not in [pd.DataFrame, EventLog, EventStream]: raise Exception("the method can be applied only to a traditional event log!")
    __event_log_deprecation_warning(log_obj)

    parameters = get_properties(
        log_obj, activity_key=activity_key, timestamp_key=timestamp_key, case_id_key=case_id_key)
    parameters["max_len"] = max_len

    from pm4py.algo.querying.llm.abstractions import log_to_cols_descr
    return log_to_cols_descr.apply(log_obj, parameters=parameters)
