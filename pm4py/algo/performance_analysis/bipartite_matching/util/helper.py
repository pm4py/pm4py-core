import re
import os
import numpy as np
from datetime import timedelta
from pm4py.objects.log.exporter.parquet import factory as parquet_exporter
from pm4py.objects.log.importer.parquet import factory as parquet_importer
from pm4py.objects.conversion.log import factory as log_conv_factory


def select_attributes(log, classifier = "concept:name"):
    """
    Select the case or event attributes of interests

    Parameters
    ------------
    log
        Event log
    classifier
        Event classifier (activity name by default)

    Returns
    ------------
    log
        Preprocessed event log
    """
    parquet_exporter.apply(log, "tmp.parquet")
    df = parquet_importer.apply("tmp.parquet",
                                parameters={"columns": ["case:concept:name", classifier, "time:timestamp"]})

    os.remove("tmp.parquet")

    return log_conv_factory.apply(df)


def index_event(log):
    """
    Index event per trace in a log

    Parameters
    ------------
    log
        Event log

    Returns
    ------------
    log
        Indexed event log
    """
    for trace in log:
        for event_index, event in enumerate(trace):
            event["eid"] = event_index + 1

    return log


def compute_weight(node_start, node_end, function=None):
    """
    Compute the weight of an edge

    Parameters
    ------------
    node_start
        Event index of starting node
    node_end
        Event index of ending node
    function
        Customized function to compute the weight
    Returns
    ------------
    weight
        Number as weight
    """
    if function is None:
        return 1 / (node_end - node_start)
    else:
        return function(node_start, node_end)


def get_edge(variable):
    """
    Get the edge with the node of numerical index

    Parameters
    ------------
    variable
        Variables of LP represented in string
    Returns
    ------------
    tuple of nodes
        Edge represented in tuple of numbers
    """
    return (int(re.split('\(|\)|,', variable.name().replace(" ", ""))[1]),
            int(re.split('\(|\)|,', variable.name().replace(" ", ""))[-2]))


def compute_time_statistics(measures):
    """
    Compute the statistics of duration

    Parameters
    ------------
    measures
        Measurement of duration
    Returns
    ------------
    stats_timedelta
        Dictionary of duration in timedelta format
    """
    total_seconds = [ts.total_seconds() for ts in measures if isinstance(ts, timedelta)]

    stats = dict()
    stats["minimum"] = round(np.min(np.array(total_seconds)))
    stats["maximum"] = round(np.max(np.array(total_seconds)))
    stats["median"] = round(np.median(np.array(total_seconds)))
    stats["mean"] = round(np.mean(np.array(total_seconds)))
    stats["std"] = round(np.std(np.array(total_seconds)))
    stats["freq"] = len(np.array(measures))

    stats_timedelta = {k: timedelta(seconds=v) for (k, v) in stats.items() if k != "freq"}
    stats_timedelta["freq"] = len(np.array(measures))

    return stats_timedelta