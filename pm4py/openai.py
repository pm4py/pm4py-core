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

from typing import Optional, Collection
import pandas as pd
from pm4py.objects.log.obj import EventLog, EventStream
from typing import Union, Tuple
from pm4py.utils import get_properties, constants
from pm4py.utils import __event_log_deprecation_warning
from pm4py.objects.ocel.obj import OCEL
from pm4py.objects.petri_net.obj import PetriNet, Marking


def describe_process(log_obj: Union[pd.DataFrame, EventLog, EventStream], api_key: Optional[str] = None, openai_model: Optional[str] = None, activity_key: str = "concept:name", timestamp_key: str = "time:timestamp", case_id_key: str = "case:concept:name") -> str:
    """
    Given an event log, provides a description of the underlying process using an OpenAI model.
    If no API key is provided, a query to be manually executed is returned.

    :param log_obj: event log
    :param api_key: API key (optional, to provide only if the query needs to be executed against the API)
    :param openai_model: OpenAI model (optional, to provide only if the query needs to be executed against the API)
    :param activity_key: the column to be used as activity
    :param timestamp_key: the column to be used as timestamp
    :param case_id_key: the column to be used as case identifier
    :rtype: ``str``

    .. code-block:: python3

        import pm4py

        log = pm4py.read_xes("tests/input_data/roadtraffic100traces.xes")
        print(pm4py.openai.describe_process(log))
    """
    if type(log_obj) not in [pd.DataFrame, EventLog, EventStream]: raise Exception("the method can be applied only to a traditional event log!")
    __event_log_deprecation_warning(log_obj)

    parameters = get_properties(
        log_obj, activity_key=activity_key, timestamp_key=timestamp_key, case_id_key=case_id_key)
    if api_key is not None:
        parameters["api_key"] = api_key
    if openai_model is not None:
        parameters["openai_model"] = openai_model

    from pm4py.algo.querying.openai import log_queries
    return log_queries.describe_process(log_obj, parameters=parameters)


def describe_path(log_obj: Union[pd.DataFrame, EventLog, EventStream], path: Tuple[str, str], api_key: Optional[str] = None, openai_model: Optional[str] = None, activity_key: str = "concept:name", timestamp_key: str = "time:timestamp", case_id_key: str = "case:concept:name") -> str:
    """
    Given an event log, provides a description of the meaning of a specified path, using an OpenAI model.
    If no API key is provided, a query to be manually executed is returned.

    :param log_obj: event log
    :param path: path to explain (e.g., ('Add Penalty', 'Send for Credit Collection') )
    :param api_key: API key (optional, to provide only if the query needs to be executed against the API)
    :param openai_model: OpenAI model (optional, to provide only if the query needs to be executed against the API)
    :param activity_key: the column to be used as activity
    :param timestamp_key: the column to be used as timestamp
    :param case_id_key: the column to be used as case identifier
    :rtype: ``str``


    .. code-block:: python3

        import pm4py

        log = pm4py.read_xes("tests/input_data/roadtraffic100traces.xes")
        print(pm4py.openai.describe_path(log, ('Add Penalty', 'Send for Credit Collection')))
    """
    if type(log_obj) not in [pd.DataFrame, EventLog, EventStream]: raise Exception("the method can be applied only to a traditional event log!")
    __event_log_deprecation_warning(log_obj)

    parameters = get_properties(
        log_obj, activity_key=activity_key, timestamp_key=timestamp_key, case_id_key=case_id_key)
    if api_key is not None:
        parameters["api_key"] = api_key
    if openai_model is not None:
        parameters["openai_model"] = openai_model

    from pm4py.algo.querying.openai import log_queries
    return log_queries.describe_path(log_obj, path, parameters=parameters)


def describe_activity(log_obj: Union[pd.DataFrame, EventLog, EventStream], activity: str, api_key: Optional[str] = None, openai_model: Optional[str] = None, activity_key: str = "concept:name", timestamp_key: str = "time:timestamp", case_id_key: str = "case:concept:name") -> str:
    """
    Given an event log, provides a description of the meaning of a specified activity, using an OpenAI model.
    If no API key is provided, a query to be manually executed is returned.

    :param log_obj: event log
    :param activity: activity to explain (e.g., 'Add Penalty' )
    :param api_key: API key (optional, to provide only if the query needs to be executed against the API)
    :param openai_model: OpenAI model (optional, to provide only if the query needs to be executed against the API)
    :param activity_key: the column to be used as activity
    :param timestamp_key: the column to be used as timestamp
    :param case_id_key: the column to be used as case identifier
    :rtype: ``str``

    .. code-block:: python3

        import pm4py

        log = pm4py.read_xes("tests/input_data/roadtraffic100traces.xes")
        print(pm4py.openai.describe_activity(log, 'Add Penalty'))
    """
    if type(log_obj) not in [pd.DataFrame, EventLog, EventStream]: raise Exception("the method can be applied only to a traditional event log!")
    __event_log_deprecation_warning(log_obj)

    parameters = get_properties(
        log_obj, activity_key=activity_key, timestamp_key=timestamp_key, case_id_key=case_id_key)
    if api_key is not None:
        parameters["api_key"] = api_key
    if openai_model is not None:
        parameters["openai_model"] = openai_model

    from pm4py.algo.querying.openai import log_queries
    return log_queries.describe_activity(log_obj, activity, parameters=parameters)


def suggest_improvements(log_obj: Union[pd.DataFrame, EventLog, EventStream], api_key: Optional[str] = None, openai_model: Optional[str] = None, activity_key: str = "concept:name", timestamp_key: str = "time:timestamp", case_id_key: str = "case:concept:name") -> str:
    """
    Given an event log, provide suggestions for the improvement of the underlying model, using an OpenAI model.
    If no API key is provided, a query to be manually executed is returned.

    :param log_obj: event log
    :param api_key: API key (optional, to provide only if the query needs to be executed against the API)
    :param openai_model: OpenAI model (optional, to provide only if the query needs to be executed against the API)
    :param activity_key: the column to be used as activity
    :param timestamp_key: the column to be used as timestamp
    :param case_id_key: the column to be used as case identifier
    :rtype: ``str``

    .. code-block:: python3

        import pm4py

        log = pm4py.read_xes("tests/input_data/roadtraffic100traces.xes")
        print(pm4py.openai.suggest_improvements(log))
    """
    if type(log_obj) not in [pd.DataFrame, EventLog, EventStream]: raise Exception("the method can be applied only to a traditional event log!")
    __event_log_deprecation_warning(log_obj)

    parameters = get_properties(
        log_obj, activity_key=activity_key, timestamp_key=timestamp_key, case_id_key=case_id_key)
    if api_key is not None:
        parameters["api_key"] = api_key
    if openai_model is not None:
        parameters["openai_model"] = openai_model

    from pm4py.algo.querying.openai import log_queries
    return log_queries.suggest_improvements(log_obj, parameters=parameters)


def code_for_log_generation(desired_process: str, api_key: Optional[str] = None, openai_model: Optional[str] = None, activity_key: str = "concept:name", timestamp_key: str = "time:timestamp", case_id_key: str = "case:concept:name") -> str:
    """
    Given the name of a desired process (for example, fast food, Purchase-to-Pay) provide code for the generation
    of an event log, using an OpenAI model.
    If no API key is provided, a query to be manually executed is returned.

    :param log_obj: event log
    :param api_key: API key (optional, to provide only if the query needs to be executed against the API)
    :param openai_model: OpenAI model (optional, to provide only if the query needs to be executed against the API)
    :param activity_key: the column to be used as activity
    :param timestamp_key: the column to be used as timestamp
    :param case_id_key: the column to be used as case identifier
    :rtype: ``str``

    .. code-block:: python3

        import pm4py

        print(pm4py.openai.code_for_log_generation('fast food'))
    """
    parameters = {}
    if api_key is not None:
        parameters["api_key"] = api_key
    if openai_model is not None:
        parameters["openai_model"] = openai_model

    from pm4py.algo.querying.openai import log_queries
    return log_queries.code_for_log_generation(desired_process, parameters=parameters)


def root_cause_analysis(log_obj: Union[pd.DataFrame, EventLog, EventStream], api_key: Optional[str] = None, openai_model: Optional[str] = None, activity_key: str = "concept:name", timestamp_key: str = "time:timestamp", case_id_key: str = "case:concept:name") -> str:
    """
    Given an event log, identifies the root causes for conformance/performance issues in the process,
    using an OpenAI model.
    If no API key is provided, a query to be manually executed is returned.

    :param log_obj: event log
    :param api_key: API key (optional, to provide only if the query needs to be executed against the API)
    :param openai_model: OpenAI model (optional, to provide only if the query needs to be executed against the API)
    :param activity_key: the column to be used as activity
    :param timestamp_key: the column to be used as timestamp
    :param case_id_key: the column to be used as case identifier
    :rtype: ``str``

    .. code-block:: python3

        import pm4py

        log = pm4py.read_xes("tests/input_data/roadtraffic100traces.xes")
        print(pm4py.openai.root_cause_analysis(log))
    """
    if type(log_obj) not in [pd.DataFrame, EventLog, EventStream]: raise Exception("the method can be applied only to a traditional event log!")
    __event_log_deprecation_warning(log_obj)

    parameters = get_properties(
        log_obj, activity_key=activity_key, timestamp_key=timestamp_key, case_id_key=case_id_key)
    if api_key is not None:
        parameters["api_key"] = api_key
    if openai_model is not None:
        parameters["openai_model"] = openai_model

    from pm4py.algo.querying.openai import log_queries
    return log_queries.root_cause_analysis(log_obj, parameters=parameters)


def describe_variant(log_obj: Union[pd.DataFrame, EventLog, EventStream], variant: Collection[str], api_key: Optional[str] = None, openai_model: Optional[str] = None, activity_key: str = "concept:name", timestamp_key: str = "time:timestamp", case_id_key: str = "case:concept:name") -> str:
    """
    Given an event log and a variant (expressed as a list/tuple of strings), describes the process execution along
    with the identification of possible anomalies in the process, using an OpenAI model.
    If no API key is provided, a query to be manually executed is returned.

    :param log_obj: event log
    :param variant: variant (expressed as a list/tuple of strings)
    :param api_key: API key (optional, to provide only if the query needs to be executed against the API)
    :param openai_model: OpenAI model (optional, to provide only if the query needs to be executed against the API)
    :param activity_key: the column to be used as activity
    :param timestamp_key: the column to be used as timestamp
    :param case_id_key: the column to be used as case identifier
    :rtype: ``str``

    .. code-block:: python3

        import pm4py

        log = pm4py.read_xes("tests/input_data/roadtraffic100traces.xes")
        print(pm4py.openai.describe_variant(log, ('Create Fine', 'Send Fine', 'Payment', 'Send for Credit Collection')))
    """
    if type(log_obj) not in [pd.DataFrame, EventLog, EventStream]: raise Exception("the method can be applied only to a traditional event log!")
    __event_log_deprecation_warning(log_obj)

    parameters = get_properties(
        log_obj, activity_key=activity_key, timestamp_key=timestamp_key, case_id_key=case_id_key)
    if api_key is not None:
        parameters["api_key"] = api_key
    if openai_model is not None:
        parameters["openai_model"] = openai_model

    from pm4py.algo.querying.openai import log_queries
    return log_queries.describe_variant(log_obj, variant, parameters=parameters)


def compare_logs(log1: Union[pd.DataFrame, EventLog, EventStream], log2: Union[pd.DataFrame, EventLog, EventStream], api_key: Optional[str] = None, openai_model: Optional[str] = None, activity_key: str = "concept:name", timestamp_key: str = "time:timestamp", case_id_key: str = "case:concept:name") -> str:
    """
    Given two event logs, perform a comparison between them, using an OpenAI model.
    If no API key is provided, a query to be manually executed is returned.

    :param log1: first event log (for the comparison)
    :param log2: event log (for the comparison)
    :param api_key: API key (optional, to provide only if the query needs to be executed against the API)
    :param openai_model: OpenAI model (optional, to provide only if the query needs to be executed against the API)
    :param activity_key: the column to be used as activity
    :param timestamp_key: the column to be used as timestamp
    :param case_id_key: the column to be used as case identifier
    :rtype: ``str``

    .. code-block:: python3

        import pm4py

        log = pm4py.read_xes("tests/input_data/roadtraffic100traces.xes")
        cases_tpa_100 = log[log["totalPaymentAmount"] > 100]["case:concept:name"].unique()
        log1 = log[~log["case:concept:name"].isin(cases_tpa_100)]
        log2 = log[log["case:concept:name"].isin(cases_tpa_100)]

        print(pm4py.openai.compare_logs(log1, log2))
    """
    if type(log1) not in [pd.DataFrame, EventLog, EventStream]: raise Exception("the method can be applied only to a traditional event log!")
    __event_log_deprecation_warning(log1)

    parameters = get_properties(
        log1, activity_key=activity_key, timestamp_key=timestamp_key, case_id_key=case_id_key)
    if api_key is not None:
        parameters["api_key"] = api_key
    if openai_model is not None:
        parameters["openai_model"] = openai_model

    from pm4py.algo.querying.openai import log_queries
    return log_queries.compare_logs(log1, log2, parameters=parameters)


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
        print(pm4py.abstract_dfg(log_obj))
    """
    if type(log_obj) not in [pd.DataFrame, EventLog, EventStream]: raise Exception("the method can be applied only to a traditional event log!")
    __event_log_deprecation_warning(log_obj)

    parameters = get_properties(
        log_obj, activity_key=activity_key, timestamp_key=timestamp_key, case_id_key=case_id_key)
    parameters["max_len"] = max_len
    parameters["include_performance"] = include_performance
    parameters["relative_frequency"] = relative_frequency
    parameters["response_header"] = response_header

    from pm4py.algo.querying.openai import log_to_dfg_descr
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
        print(pm4py.abstract_variants(log_obj))
    """
    if type(log_obj) not in [pd.DataFrame, EventLog, EventStream]: raise Exception("the method can be applied only to a traditional event log!")
    __event_log_deprecation_warning(log_obj)

    parameters = get_properties(
        log_obj, activity_key=activity_key, timestamp_key=timestamp_key, case_id_key=case_id_key)
    parameters["max_len"] = max_len
    parameters["include_performance"] = include_performance
    parameters["relative_frequency"] = relative_frequency
    parameters["response_header"] = response_header

    from pm4py.algo.querying.openai import log_to_variants_descr
    return log_to_variants_descr.apply(log_obj, parameters=parameters)


def abstract_ocel(ocel: OCEL, include_timestamps: bool = True) -> str:
    """
    Obtains the abstraction of an object-centric event log

    :param ocel: object-centric event log
    :param include_timestamps: (boolean) includes the timestamp information in the abstraction
    :rtype: ``str``

    .. code-block:: python3

        import pm4py

        ocel = pm4py.read_ocel("tests/input_data/ocel/example_log.jsonocel")
        print(pm4py.abstract_ocel(ocel))
    """
    parameters = {}
    parameters["include_timestamps"] = include_timestamps

    from pm4py.algo.transformation.ocel.description import algorithm as ocel_description
    return ocel_description.apply(ocel, parameters=parameters)


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
        print(pm4py.abstract_event_stream(log_obj))
    """
    if type(log_obj) not in [pd.DataFrame, EventLog, EventStream]: raise Exception("the method can be applied only to a traditional event log!")
    __event_log_deprecation_warning(log_obj)

    parameters = get_properties(
        log_obj, activity_key=activity_key, timestamp_key=timestamp_key, case_id_key=case_id_key)
    parameters["max_len"] = max_len
    parameters["response_header"] = response_header

    from pm4py.algo.querying.openai import stream_to_descr
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
        print(pm4py.openai.abstract_petri_net(net, im, fm))
    """
    parameters = {}
    parameters["response_header"] = response_header

    from pm4py.algo.querying.openai import net_to_descr
    return net_to_descr.apply(net, im, fm, parameters=parameters)


def anomaly_detection(log_obj: Union[pd.DataFrame, EventLog, EventStream], api_key: Optional[str] = None, openai_model: Optional[str] = None, activity_key: str = "concept:name", timestamp_key: str = "time:timestamp", case_id_key: str = "case:concept:name") -> str:
    """
    Given an event log, identifies the main anomalous variants in the process,
    using an OpenAI model.
    If no API key is provided, a query to be manually executed is returned.

    :param log_obj: event log
    :param api_key: API key (optional, to provide only if the query needs to be executed against the API)
    :param openai_model: OpenAI model (optional, to provide only if the query needs to be executed against the API)
    :param activity_key: the column to be used as activity
    :param timestamp_key: the column to be used as timestamp
    :param case_id_key: the column to be used as case identifier
    :rtype: ``str``

    .. code-block:: python3

        import pm4py

        log = pm4py.read_xes("tests/input_data/roadtraffic100traces.xes")
        print(pm4py.openai.anomaly_detection(log))
    """
    if type(log_obj) not in [pd.DataFrame, EventLog, EventStream]: raise Exception("the method can be applied only to a traditional event log!")
    __event_log_deprecation_warning(log_obj)

    parameters = get_properties(
        log_obj, activity_key=activity_key, timestamp_key=timestamp_key, case_id_key=case_id_key)
    if api_key is not None:
        parameters["api_key"] = api_key
    if openai_model is not None:
        parameters["openai_model"] = openai_model

    from pm4py.algo.querying.openai import log_queries
    return log_queries.anomaly_detection(log_obj, parameters=parameters)


def suggest_clusters(log_obj: Union[pd.DataFrame, EventLog, EventStream], api_key: Optional[str] = None, openai_model: Optional[str] = None, activity_key: str = "concept:name", timestamp_key: str = "time:timestamp", case_id_key: str = "case:concept:name") -> str:
    """
    Given an event log, identifies the main clusters of variants in the process.
    If no API key is provided, a query to be manually executed is returned.

    :param log_obj: event log
    :param api_key: API key (optional, to provide only if the query needs to be executed against the API)
    :param openai_model: OpenAI model (optional, to provide only if the query needs to be executed against the API)
    :param activity_key: the column to be used as activity
    :param timestamp_key: the column to be used as timestamp
    :param case_id_key: the column to be used as case identifier
    :rtype: ``str``

    .. code-block:: python3

        import pm4py

        log = pm4py.read_xes("tests/input_data/roadtraffic100traces.xes")
        print(pm4py.openai.suggest_clusters(log))
    """
    if type(log_obj) not in [pd.DataFrame, EventLog, EventStream]: raise Exception("the method can be applied only to a traditional event log!")
    __event_log_deprecation_warning(log_obj)

    parameters = get_properties(
        log_obj, activity_key=activity_key, timestamp_key=timestamp_key, case_id_key=case_id_key)
    if api_key is not None:
        parameters["api_key"] = api_key
    if openai_model is not None:
        parameters["openai_model"] = openai_model

    from pm4py.algo.querying.openai import log_queries
    return log_queries.suggest_clusters(log_obj, parameters=parameters)


def conformance_checking(log_obj: Union[pd.DataFrame, EventLog, EventStream], rule: str, api_key: Optional[str] = None, openai_model: Optional[str] = None, activity_key: str = "concept:name", timestamp_key: str = "time:timestamp", case_id_key: str = "case:concept:name") -> str:
    """
    Given an event log and a conformance rule, measures the level of fitness of the log
    against the rule, and identify violating variants.

    :param log_obj: event log
    :param rule: conformance checking rule
    :param api_key: API key (optional, to provide only if the query needs to be executed against the API)
    :param openai_model: OpenAI model (optional, to provide only if the query needs to be executed against the API)
    :param activity_key: the column to be used as activity
    :param timestamp_key: the column to be used as timestamp
    :param case_id_key: the column to be used as case identifier
    :rtype: ``str``

    .. code-block:: python3

        import pm4py

        log = pm4py.read_xes("tests/input_data/roadtraffic100traces.xes")
        print(pm4py.openai.conformance_checking(log, 'all traces should have a single payment'))
    """
    if type(log_obj) not in [pd.DataFrame, EventLog, EventStream]: raise Exception("the method can be applied only to a traditional event log!")
    __event_log_deprecation_warning(log_obj)

    parameters = get_properties(
        log_obj, activity_key=activity_key, timestamp_key=timestamp_key, case_id_key=case_id_key)
    if api_key is not None:
        parameters["api_key"] = api_key
    if openai_model is not None:
        parameters["openai_model"] = openai_model

    from pm4py.algo.querying.openai import log_queries
    return log_queries.conformance_checking(log_obj, rule, parameters=parameters)


def suggest_verify_hypotheses(log_obj: Union[pd.DataFrame, EventLog, EventStream], max_len: int = constants.OPENAI_MAX_LEN // 2, api_key: Optional[str] = None, openai_model: Optional[str] = None, activity_key: str = "concept:name", timestamp_key: str = "time:timestamp", case_id_key: str = "case:concept:name") -> str:
    """
    Given an event log, identifies some hypotheses to verify against the data.

    :param log_obj: event log
    :param max_len: maximum length of the (string) abstraction
    :param api_key: API key (optional, to provide only if the query needs to be executed against the API)
    :param openai_model: OpenAI model (optional, to provide only if the query needs to be executed against the API)
    :param activity_key: the column to be used as activity
    :param timestamp_key: the column to be used as timestamp
    :param case_id_key: the column to be used as case identifier
    :rtype: ``str``

    .. code-block:: python3

        import pm4py

        log = pm4py.read_xes("tests/input_data/roadtraffic100traces.xes")
        print(pm4py.openai.suggest_verify_hypotheses(log))
    """
    if type(log_obj) not in [pd.DataFrame, EventLog, EventStream]: raise Exception("the method can be applied only to a traditional event log!")
    __event_log_deprecation_warning(log_obj)

    parameters = get_properties(
        log_obj, activity_key=activity_key, timestamp_key=timestamp_key, case_id_key=case_id_key)
    parameters["max_len"] = max_len
    if api_key is not None:
        parameters["api_key"] = api_key
    if openai_model is not None:
        parameters["openai_model"] = openai_model

    from pm4py.algo.querying.openai import log_queries
    return log_queries.suggest_verify_hypotheses(log_obj, parameters=parameters)


def filtering_query(log_obj: Union[pd.DataFrame, EventLog, EventStream], filtering_query: str,  max_len: int = constants.OPENAI_MAX_LEN // 2, api_key: Optional[str] = None, openai_model: Optional[str] = None, activity_key: str = "concept:name", timestamp_key: str = "time:timestamp", case_id_key: str = "case:concept:name") -> str:
    """
    Given an event log, performs a query to filter the event data

    :param log_obj: event log
    :param filtering_query: query to filter the event data
    :param max_len: maximum length of the (string) abstraction
    :param api_key: API key (optional, to provide only if the query needs to be executed against the API)
    :param openai_model: OpenAI model (optional, to provide only if the query needs to be executed against the API)
    :param activity_key: the column to be used as activity
    :param timestamp_key: the column to be used as timestamp
    :param case_id_key: the column to be used as case identifier
    :rtype: ``str``

    .. code-block:: python3

        import pm4py

        log = pm4py.read_xes("tests/input_data/roadtraffic100traces.xes")
        print(pm4py.openai.filtering_query(log, 'filter the events where the amount is greater than 100'))
    """
    if type(log_obj) not in [pd.DataFrame, EventLog, EventStream]: raise Exception("the method can be applied only to a traditional event log!")
    __event_log_deprecation_warning(log_obj)

    parameters = get_properties(
        log_obj, activity_key=activity_key, timestamp_key=timestamp_key, case_id_key=case_id_key)
    if api_key is not None:
        parameters["api_key"] = api_key
    if openai_model is not None:
        parameters["openai_model"] = openai_model
    parameters["max_len"] = max_len

    from pm4py.algo.querying.openai import log_queries
    return log_queries.filtering_query(log_obj, filtering_query, parameters=parameters)
