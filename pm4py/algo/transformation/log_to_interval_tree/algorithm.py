from enum import Enum
from typing import Optional, Dict, Any

from intervaltree import IntervalTree

from pm4py.algo.transformation.log_to_interval_tree.variants import open_paths
from pm4py.objects.log.obj import EventLog
from pm4py.util import exec_utils
from pm4py.objects.conversion.log import converter as log_converter


class Variants(Enum):
    OPEN_PATHS = open_paths


def apply(log: EventLog, variant=Variants.OPEN_PATHS, parameters: Optional[Dict[Any, Any]] = None) -> IntervalTree:
    """
    Transforms the event log to an interval tree using one of the available variants

    Parameters
    -----------------
    log
        Event log
    variant
        Variant of the algorithm to be used:
        - Variants.OPEN_PATHS: transforms the event log to an interval tree in which the intervals are the
                directly-follows paths in the log (open at the complete timestamp of the source event,
                and closed at the start timestamp of the target event),
                 and having as associated data the source and the target event.

    Returns
    -----------------
    tree
        Interval tree object (which can be queried at a given timestamp, or range of timestamps)
    """
    log = log_converter.apply(log, variant=log_converter.Variants.TO_EVENT_LOG, parameters=parameters)
    return exec_utils.get_variant(variant).apply(log, parameters=parameters)
