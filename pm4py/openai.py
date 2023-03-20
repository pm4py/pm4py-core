from typing import Optional, Collection
import pandas as pd
from pm4py.objects.log.obj import EventLog, EventStream
from typing import Union, Tuple


def describe_process(log_obj: Union[pd.DataFrame, EventLog, EventStream], api_key: Optional[str] = None, openai_model: Optional[str] = None) -> str:
    """
    Given an event log, provides a description of the underlying process using an OpenAI model.
    If no API key is provided, a query to be manually executed is returned.

    :param log_obj: event log
    :param api_key: API key (optional, to provide only if the query needs to be executed against the API)
    :param openai_model: OpenAI model (optional, to provide only if the query needs to be executed against the API)
    :rtype: ``str``

    .. code-block:: python3

        import pm4py

        log = pm4py.read_xes("tests/input_data/roadtraffic100traces.xes")
        print(pm4py.openai.describe_process(log))
    """
    from pm4py.algo.querying.openai import log_queries
    return log_queries.describe_process(log_obj, parameters={"api_key": api_key, "openai_model": openai_model})


def describe_path(log_obj: Union[pd.DataFrame, EventLog, EventStream], path: Tuple[str, str], api_key: Optional[str] = None, openai_model: Optional[str] = None) -> str:
    """
    Given an event log, provides a description of the meaning of a specified path, using an OpenAI model.
    If no API key is provided, a query to be manually executed is returned.

    :param log_obj: event log
    :param path: path to explain (e.g., ('Add Penalty', 'Send for Credit Collection') )
    :param api_key: API key (optional, to provide only if the query needs to be executed against the API)
    :param openai_model: OpenAI model (optional, to provide only if the query needs to be executed against the API)
    :rtype: ``str``


    .. code-block:: python3

        import pm4py

        log = pm4py.read_xes("tests/input_data/roadtraffic100traces.xes")
        print(pm4py.openai.describe_path(log, ('Add Penalty', 'Send for Credit Collection')))
    """
    from pm4py.algo.querying.openai import log_queries
    return log_queries.describe_path(log_obj, path, parameters={"api_key": api_key, "openai_model": openai_model})


def describe_activity(log_obj: Union[pd.DataFrame, EventLog, EventStream], activity: str, api_key: Optional[str] = None, openai_model: Optional[str] = None) -> str:
    """
    Given an event log, provides a description of the meaning of a specified activity, using an OpenAI model.
    If no API key is provided, a query to be manually executed is returned.

    :param log_obj: event log
    :param activity: activity to explain (e.g., 'Add Penalty' )
    :param api_key: API key (optional, to provide only if the query needs to be executed against the API)
    :param openai_model: OpenAI model (optional, to provide only if the query needs to be executed against the API)
    :rtype: ``str``

    .. code-block:: python3

        import pm4py

        log = pm4py.read_xes("tests/input_data/roadtraffic100traces.xes")
        print(pm4py.openai.describe_activity(log, 'Add Penalty'))
    """
    from pm4py.algo.querying.openai import log_queries
    return log_queries.describe_activity(log_obj, activity, parameters={"api_key": api_key, "openai_model": openai_model})


def suggest_improvements(log_obj: Union[pd.DataFrame, EventLog, EventStream], api_key: Optional[str] = None, openai_model: Optional[str] = None) -> str:
    """
    Given an event log, provide suggestions for the improvement of the underlying model, using an OpenAI model.
    If no API key is provided, a query to be manually executed is returned.

    :param log_obj: event log
    :param api_key: API key (optional, to provide only if the query needs to be executed against the API)
    :param openai_model: OpenAI model (optional, to provide only if the query needs to be executed against the API)
    :rtype: ``str``

    .. code-block:: python3

        import pm4py

        log = pm4py.read_xes("tests/input_data/roadtraffic100traces.xes")
        print(pm4py.openai.suggest_improvements(log))
    """
    from pm4py.algo.querying.openai import log_queries
    return log_queries.suggest_improvements(log_obj, parameters={"api_key": api_key, "openai_model": openai_model})


def code_for_log_generation(desired_process: str, api_key: Optional[str] = None, openai_model: Optional[str] = None) -> str:
    """
    Given the name of a desired process (for example, fast food, Purchase-to-Pay) provide code for the generation
    of an event log, using an OpenAI model.
    If no API key is provided, a query to be manually executed is returned.

    :param log_obj: event log
    :param api_key: API key (optional, to provide only if the query needs to be executed against the API)
    :param openai_model: OpenAI model (optional, to provide only if the query needs to be executed against the API)
    :rtype: ``str``

    .. code-block:: python3

        import pm4py

        print(pm4py.openai.code_for_log_generation('fast food'))
    """
    from pm4py.algo.querying.openai import log_queries
    return log_queries.code_for_log_generation(desired_process, parameters={"api_key": api_key, "openai_model": openai_model})


def root_cause_analysis(log_obj: Union[pd.DataFrame, EventLog, EventStream], api_key: Optional[str] = None, openai_model: Optional[str] = None) -> str:
    """
    Given an event log, identifies the root causes for conformance/performance issues in the process,
    using an OpenAI model.
    If no API key is provided, a query to be manually executed is returned.

    :param log_obj: event log
    :param api_key: API key (optional, to provide only if the query needs to be executed against the API)
    :param openai_model: OpenAI model (optional, to provide only if the query needs to be executed against the API)
    :rtype: ``str``

    .. code-block:: python3

        import pm4py

        log = pm4py.read_xes("tests/input_data/roadtraffic100traces.xes")
        print(pm4py.openai.root_cause_analysis(log))
    """
    from pm4py.algo.querying.openai import log_queries
    return log_queries.root_cause_analysis(log_obj, parameters={"api_key": api_key, "openai_model": openai_model})


def describe_variant(log_obj: Union[pd.DataFrame, EventLog, EventStream], variant: Collection[str], api_key: Optional[str] = None, openai_model: Optional[str] = None) -> str:
    """
    Given an event log and a variant (expressed as a list/tuple of strings), describes the process execution along
    with the identification of possible anomalies in the process, using an OpenAI model.
    If no API key is provided, a query to be manually executed is returned.

    :param log_obj: event log
    :param variant: variant (expressed as a list/tuple of strings)
    :param api_key: API key (optional, to provide only if the query needs to be executed against the API)
    :param openai_model: OpenAI model (optional, to provide only if the query needs to be executed against the API)
    :rtype: ``str``

    .. code-block:: python3

        import pm4py

        log = pm4py.read_xes("tests/input_data/roadtraffic100traces.xes")
        print(pm4py.openai.describe_variant(log, ('Create Fine', 'Send Fine', 'Payment', 'Send for Credit Collection')))
    """
    from pm4py.algo.querying.openai import log_queries
    return log_queries.describe_variant(log_obj, variant, parameters={"api_key": api_key, "openai_model": openai_model})


def compare_logs(log1: Union[pd.DataFrame, EventLog, EventStream], log2: Union[pd.DataFrame, EventLog, EventStream], api_key: Optional[str] = None, openai_model: Optional[str] = None) -> str:
    """
    Given two event logs, perform a comparison between them, using an OpenAI model.
    If no API key is provided, a query to be manually executed is returned.

    :param log1: first event log (for the comparison)
    :param log2: event log (for the comparison)
    :param api_key: API key (optional, to provide only if the query needs to be executed against the API)
    :param openai_model: OpenAI model (optional, to provide only if the query needs to be executed against the API)
    :rtype: ``str``

    .. code-block:: python3

        import pm4py

        log = pm4py.read_xes("tests/input_data/roadtraffic100traces.xes")
        cases_tpa_100 = log[log["totalPaymentAmount"] > 100]["case:concept:name"].unique()
        log1 = log[~log["case:concept:name"].isin(cases_tpa_100)]
        log2 = log[log["case:concept:name"].isin(cases_tpa_100)]

        print(pm4py.openai.compare_logs(log1, log2))
    """
    from pm4py.algo.querying.openai import log_queries
    return log_queries.compare_logs(log1, log2, parameters={"api_key": api_key, "openai_model": openai_model})
