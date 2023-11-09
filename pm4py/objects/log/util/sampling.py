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
import random

from pm4py.objects.log.obj import EventStream, EventLog


def sample_stream(event_log, no_events=100):
    """
    Randomly sample a fixed number of events from the original event log

    Parameters
    -----------
    event_log
        Event log
    no_events
        Number of events that the sample should have

    Returns
    -----------
    newLog
        Filtered log
    """
    new_log = EventStream(attributes=event_log.attributes, extensions=event_log.extensions, globals=event_log.omni_present,
                          classifiers=event_log.classifiers)
    new_log._list = random.sample(event_log, min(no_events, len(event_log)))
    return new_log


def sample_log(log, no_traces=100):
    """
    Randomly sample a fixed number of traces from the original log

    Parameters
    -----------
    log
        Log
    no_traces
        Number of traces that the sample should have

    Returns
    -----------
    newLog
        Filtered log
    """
    new_log = EventLog(attributes=log.attributes, extensions=log.extensions, globals=log.omni_present,
                       classifiers=log.classifiers, properties=log.properties)
    new_log._list = random.sample(log, min(no_traces, len(log)))
    return new_log


def sample(log, n=100):
    """
    Randomly sample a fixed number of traces from the original log

    Parameters
    -----------
    log
        Trace/event log
    n
        Number of elements that the sample should have

    Returns
    -----------
    newLog
        Filtered log
    """

    if type(log) is EventLog:
        return sample_log(log, no_traces=n)

    return sample_stream(log, no_events=n)
