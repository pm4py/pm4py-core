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
