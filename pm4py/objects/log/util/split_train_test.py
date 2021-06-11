from pm4py.objects.log.obj import EventLog
from typing import Tuple
import random
import math


def split(log: EventLog, train_percentage: float = 0.8) -> Tuple[EventLog, EventLog]:
    """
    Split an event log in a training log and a test log (for machine learning purposes)

    Parameters
    --------------
    log
        Event log
    train_percentage
        Fraction of traces to be included in the training log (from 0.0 to 1.0)

    Returns
    --------------
    training_log
        Training event log
    test_log
        Test event log
    """
    idxs = [i for i in range(len(log))]
    random.shuffle(idxs)
    stop_idx = math.floor(len(idxs) * train_percentage) + 1
    idxs_train = idxs[:stop_idx]
    idxs_test = idxs[stop_idx:]
    train_log = EventLog(list(), attributes=log.attributes, extensions=log.extensions, classifiers=log.classifiers,
                            omni_present=log.omni_present, properties=log.properties)
    test_log = EventLog(list(), attributes=log.attributes, extensions=log.extensions, classifiers=log.classifiers,
                            omni_present=log.omni_present, properties=log.properties)
    for idx in idxs_train:
        train_log.append(log[idx])
    for idx in idxs_test:
        test_log.append(log[idx])
    return train_log, test_log
