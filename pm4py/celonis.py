from pycelonis.ems.data_integration.data_pool import DataPool, DataModel
from pycelonis.celonis import DataIntegration, Celonis
from typing import Union
import pandas as pd
from pm4py.objects.ocel.obj import OCEL
from pm4py.objects.log.obj import EventLog, EventStream


def read_log(data_pool: DataPool, data_model: DataModel) -> pd.DataFrame:
    """
    Reads a traditional event log from a Celonis data model

    :param data_pool: Celonis data pool
    :param data_model: Celonis data model
    :rtype: ``pd.DataFrame``

    .. code-block:: python3

        import pm4py
        import pm4py.celonis

        c = ...
        data_pool = ...
        data_model = ...

        dataframe = pm4py.celonis.read_log(data_pool, data_model)
    """
    from pm4py.algo.celonis.retrieval import log_retrieval
    return log_retrieval.apply(data_pool, data_model)


def read_ocel(data_pool: DataPool, data_model: DataModel) -> OCEL:
    """
    Reads an OCEL from a Celonis data model (used for the ProcessSphere feature)

    :param data_pool: Celonis data pool
    :param data_model: Celonis data model
    :rtype: ``OCEL``

    .. code-block:: python3

        import pm4py
        import pm4py.celonis

        c = ...
        data_pool = ...
        data_model = ...

        dataframe = pm4py.celonis.read_ocel(data_pool, data_model)
    """
    from pm4py.algo.celonis.retrieval import ocel_retrieval
    return ocel_retrieval.apply(data_pool, data_model)


def write_log(log: Union[EventLog, EventStream, pd.DataFrame], c: Union[Celonis, DataIntegration],
              data_pool_name: str) -> DataModel:
    """
    Uploads a traditional event log to a Celonis instance, given the specification of the name of the target data pool

    :param log: log object
    :param c: Celonis data integration
    :param data_pool_name: name of the target data pool
    :rtype: ``DataModel``

    .. code-block:: python3

        import pm4py
        import pm4py.celonis

        c = ...
        log = pm4py.read_xes('tests/input_data/running-example.xes')

        data_model = pm4py.celonis.write_log(log, c, 'running example DP')
    """
    from pm4py.algo.celonis.upload import log_upload
    return log_upload.apply(log, c, data_pool_name)


def write_ocel(ocel: OCEL, c: Union[Celonis, DataIntegration], data_pool_name: str) -> DataModel:
    """
    Uploads an OCEL to a Celonis instance, given the specification of the name of the target data pool

    :param ocel: object-centric event log
    :param c: Celonis data integration
    :param data_pool_name: name of the target data pool
    :rtype: ``DataModel``

    .. code-block:: python3

        import pm4py
        import pm4py.celonis

        c = ...
        ocel = pm4py.read_ocel('tests/input_data/ocel/example_log.jsonocel')

        data_model = pm4py.celonis.write_ocel(ocel, c, 'ocel DP')
    """
    from pm4py.algo.celonis.upload import ocel_upload
    return ocel_upload.apply(ocel, c, data_pool_name)
