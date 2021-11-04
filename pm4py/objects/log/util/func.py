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

import deprecation

from pm4py.meta import VERSION
from pm4py.objects.log import obj as log_inst


@deprecation.deprecated(deprecated_in='2.1.3.1', removed_in='2.4.0', current_version=VERSION,
                        details='filter_() deprecated, use pm4py.filter_log() or pm4py.filter_trace() instead')
def filter_(func, log):
    '''
    Filters the log according to a given lambda function.

    Parameters
    ----------
    func
    log

    Returns
    -------

    '''
    if isinstance(log, log_inst.EventLog):
        return log_inst.EventLog(list(filter(func, log)), attributes=log.attributes, classifiers=log.classifiers,
                                 omni_present=log.omni_present, extensions=log.extensions, properties=log.properties)
    elif isinstance(log, log_inst.EventStream):
        return log_inst.EventStream(list(filter(func, log)), attributes=log.attributes, classifiers=log.classifiers,
                                    omni_present=log.omni_present, extensions=log.extensions, properties=log.properties)
    else:
        warnings.warn('input log object not of appropriate type, filter() not applied')
        return log


@deprecation.deprecated(deprecated_in='2.1.3.1', removed_in='2.4.0', current_version=VERSION,
                        details='map_() deprecated, use pm4py.map_log() or pm4py.map_trace() instead')
def map_(func, log):
    '''
        Maps the log according to a given lambda function.
        domain and target of the function need to be of the same type (either trace or event) otherwise, the map behaves unexpected

        Parameters
        ----------
        func
        log

        Returns
        -------

        '''
    if isinstance(log, log_inst.EventLog):
        return log_inst.EventLog(list(map(func, log)), attributes=log.attributes, classifiers=log.classifiers,
                                 omni_present=log.omni_present, extensions=log.extensions, properties=log.properties)
    elif isinstance(log, log_inst.EventStream):
        return log_inst.EventStream(list(map(func, log)), attributes=log.attributes, classifiers=log.classifiers,
                                    omni_present=log.omni_present, extensions=log.extensions, properties=log.properties)
    else:
        warnings.warn('input log object not of appropriate type, map() not applied')
        return log


@deprecation.deprecated(deprecated_in='2.1.3.1', removed_in='2.4.0', current_version=VERSION,
                        details='sort_() deprecated, use pm4py.sort_log() or pm4py.sort_trace() instead')
def sort_(func, log, reverse=False):
    if isinstance(log, log_inst.EventLog):
        return log_inst.EventLog(sorted(log, key=func, reverse=reverse), attributes=log.attributes,
                                 classifiers=log.classifiers, omni_present=log.omni_present, extensions=log.extensions, properties=log.properties)
    elif isinstance(log, log_inst.EventStream):
        return log_inst.EventStream(sorted(log, key=func, reverse=reverse), attributes=log.attributes,
                                    classifiers=log.classifiers,
                                    omni_present=log.omni_present, extensions=log.extensions, properties=log.properties)
    else:
        warnings.warn('input log object not of appropriate type, map() not applied')
        return log
