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
__doc__ = """
"""

import warnings
from pm4py.util import constants
from typing import Callable, Any, Union

from pm4py.objects.log import obj as log_inst
from pm4py.utils import __event_log_deprecation_warning
import deprecation


@deprecation.deprecated(deprecated_in="2.3.0", removed_in="3.0.0", details="the EventLog class will be removed in a future release.")
def filter_log(f: Callable[[Any], bool], log: log_inst.EventLog) -> Union[log_inst.EventLog, log_inst.EventStream]:
    """
    Filters the log according to a given (lambda) function.

    :param f: function that specifies the filter criterion, may be a lambda
    :param log: event log; either EventLog or EventStream Object
    :rtype: ``Union[log_inst.EventLog, log_inst.EventStream]``
    """
    __event_log_deprecation_warning(log)

    if isinstance(log, log_inst.EventLog):
        return log_inst.EventLog(list(filter(f, log)), attributes=log.attributes, classifiers=log.classifiers,
                                 omni_present=log.omni_present, extensions=log.extensions, properties=log.properties)
    elif isinstance(log, log_inst.EventStream):
        return log_inst.EventStream(list(filter(f, log)), attributes=log.attributes, classifiers=log.classifiers,
                                    omni_present=log.omni_present, extensions=log.extensions, properties=log.properties)
    else:
        if constants.SHOW_INTERNAL_WARNINGS:
            warnings.warn('input log object not of appropriate type, filter() not applied')
        return log


def filter_trace(f: Callable[[Any], bool], trace: log_inst.Trace) -> log_inst.Trace:
    """
    Filters the trace according to a given (lambda) function.

    :param f: function that specifies the filter criterion, may be a lambda
    :param trace: trace; PM4Py trace object
    :rtype: ``log_inst.Trace``
    """
    __event_log_deprecation_warning(trace)

    if isinstance(trace, log_inst.Trace):
        return log_inst.Trace(list(filter(f, trace)), attributes=trace.attributes)
    else:
        if constants.SHOW_INTERNAL_WARNINGS:
            warnings.warn('input trace object is not of the appropriate type, filter() not applied')
        return trace


@deprecation.deprecated(deprecated_in="2.3.0", removed_in="3.0.0", details="the EventLog class will be removed in a future release.")
def sort_log(log: log_inst.EventLog, key, reverse: bool = False) -> Union[log_inst.EventLog, log_inst.EventStream]:
    """
    Sorts the event log according to a given key.

    :param log: event log object; either EventLog or EventStream
    :param key: sorting key
    :param reverse: indicates whether sorting should be reversed or not
    :rtype: ``Union[log_inst.EventLog, log_inst.EventStream]``
    """
    __event_log_deprecation_warning(log)

    if isinstance(log, log_inst.EventLog):
        return log_inst.EventLog(sorted(log, key=key, reverse=reverse), attributes=log.attributes,
                                 classifiers=log.classifiers, omni_present=log.omni_present, extensions=log.extensions, properties=log.properties)
    elif isinstance(log, log_inst.EventStream):
        return log_inst.EventStream(sorted(log, key=key, reverse=reverse), attributes=log.attributes,
                                    classifiers=log.classifiers,
                                    omni_present=log.omni_present, extensions=log.extensions, properties=log.properties)
    else:
        if constants.SHOW_INTERNAL_WARNINGS:
            warnings.warn('input log object not of appropriate type, sorted() not applied')
        return log


@deprecation.deprecated(deprecated_in="2.3.0", removed_in="3.0.0", details="the EventLog class will be removed in a future release.")
def sort_trace(trace: log_inst.Trace, key, reverse: bool = False) -> log_inst.Trace:
    """
    Sorts the events in a trace according to a given key.

    :param trace: input trace
    :param key: sorting key
    :param reverse: indicates whether sorting should be reversed (default False)
    :rtype: ``log_inst.Trace``
    """
    __event_log_deprecation_warning(trace)

    if isinstance(trace, log_inst.Trace):
        return log_inst.Trace(sorted(trace, key=key, reverse=reverse))
    else:
        if constants.SHOW_INTERNAL_WARNINGS:
            warnings.warn('input trace object not of appropriate type, sorted() not applied')
        return trace
