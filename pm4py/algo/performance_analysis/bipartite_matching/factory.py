from pm4py.algo.performance_analysis.bipartite_matching.versions import classic
from pm4py.objects.log.log import EventLog
import pm4py.algo.performance_analysis.bipartite_matching.util.shared_variables as sv
from pm4py.objects.conversion.log import factory as log_conv_factory

def apply(log, start, end, classifier = "concept:name"):
    """
    Measure the duration of a log

    Parameters
    ------------
    log
        Event log
    start
        Start activities
    end
        End activities
    classifier
        Event classifier (activity name by default)
    Returns
    ------------
    result
        Case ID: (edges selected, statistical result)
    """
    return classic.apply(log_conv_factory.apply(log), start, end, classifier)


def update(start, end):
    """
    Measure the duration of a log

    Parameters
    ------------
    start
        Start activities
    end
        End activities
    Returns
    ------------
    result
        Case ID: (edges selected, statistical result)
    """
    return classic.update(start, end)


def get_indexed_log():
    """
    Get the indexed log for visualization

    Returns
    ------------
    indexed_log
        Event log with events indexed based on the order in a trace
    """
    return sv.indexed_log

