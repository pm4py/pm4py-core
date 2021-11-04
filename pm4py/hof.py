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
import warnings
from typing import Callable, Any, Union

from pm4py.objects.log import obj as log_inst
from pm4py.utils import general_checks_classical_event_log


def filter_log(f: Callable[[Any], bool], log: log_inst.EventLog) -> Union[log_inst.EventLog, log_inst.EventStream]:
    """
    Filters the log according to a given (lambda) function.

    Parameters
    ----------
    f
        function that specifies the filter criterion, may be a lambda
    log
        event log; either EventLog or EventStream Object

    Returns
    -------
    log
        filtered event log if object provided is correct; original log if not correct

    """
    general_checks_classical_event_log(log)
    if isinstance(log, log_inst.EventLog):
        return log_inst.EventLog(list(filter(f, log)), attributes=log.attributes, classifiers=log.classifiers,
                                 omni_present=log.omni_present, extensions=log.extensions, properties=log.properties)
    elif isinstance(log, log_inst.EventStream):
        return log_inst.EventStream(list(filter(f, log)), attributes=log.attributes, classifiers=log.classifiers,
                                    omni_present=log.omni_present, extensions=log.extensions, properties=log.properties)
    else:
        warnings.warn('input log object not of appropriate type, filter() not applied')
        return log


def filter_trace(f: Callable[[Any], bool], trace: log_inst.Trace) -> log_inst.Trace:
    """
    Filters the trace according to a given (lambda) function.

    Parameters
    ----------
    f
        function that specifies the filter criterion, may be a lambda
    trace
        trace; PM4Py trace object

    Returns
    -------
    trace
        filtered trace if object provided is correct; original log if not correct
    """
    if isinstance(trace, log_inst.Trace):
        return log_inst.Trace(list(filter(f, trace)), attributes=trace.attributes)
    else:
        warnings.warn('input trace object is not of the appropriate type, filter() not applied')


def sort_log(log: log_inst.EventLog, key, reverse: bool = False) -> Union[log_inst.EventLog, log_inst.EventStream]:
    """
    Sorts the event log according to a given key.

    Parameters
    ----------
    log
        event log object; either EventLog or EventStream
    key
        sorting key
    reverse
        indicates whether sorting should be reversed or not

    Returns
    -------
        sorted event log if object provided is correct; original log if not correct
    """
    general_checks_classical_event_log(log)
    if isinstance(log, log_inst.EventLog):
        return log_inst.EventLog(sorted(log, key=key, reverse=reverse), attributes=log.attributes,
                                 classifiers=log.classifiers, omni_present=log.omni_present, extensions=log.extensions, properties=log.properties)
    elif isinstance(log, log_inst.EventStream):
        return log_inst.EventStream(sorted(log, key=key, reverse=reverse), attributes=log.attributes,
                                    classifiers=log.classifiers,
                                    omni_present=log.omni_present, extensions=log.extensions, properties=log.properties)
    else:
        warnings.warn('input log object not of appropriate type, sorted() not applied')
        return log


def sort_trace(trace: log_inst.Trace, key, reverse: bool = False) -> log_inst.Trace:
    """

    Parameters
    ----------
    trace
        input trace
    key
        sorting key
    reverse
        indicate whether sorting should be reversed (default False)

    Returns
    -------
        sorted trace if object provided is correct; original log if not correct
    """
    if isinstance(trace, log_inst.Trace):
        return log_inst.Trace(sorted(trace, key=key, reverse=reverse))
    else:
        warnings.warn('input trace object not of appropriate type, sorted() not applied')
        return trace
