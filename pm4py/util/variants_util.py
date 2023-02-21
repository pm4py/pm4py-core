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
from pm4py.util import exec_utils, constants, xes_constants
from enum import Enum


class Parameters(Enum):
    ACTIVITY_KEY = constants.PARAMETER_CONSTANT_ACTIVITY_KEY
    PARAMETER_VARIANT_DELIMITER = "variant_delimiter"


def variant_to_trace(variant, parameters=None):
    if parameters is None:
        parameters = {}

    activity_key = exec_utils.get_param_value(Parameters.ACTIVITY_KEY, parameters, xes_constants.DEFAULT_NAME_KEY)
    variant_delimiter = exec_utils.get_param_value(Parameters.PARAMETER_VARIANT_DELIMITER, parameters,
                                                   constants.DEFAULT_VARIANT_SEP)

    from pm4py.objects.log.obj import Trace, Event

    trace = Trace()
    if type(variant) is tuple or type(variant) is list:
        for act in variant:
            event = Event({activity_key: act})
            trace.append(event)
    elif type(variant) is str:
        var_act = variant.split(variant_delimiter)
        for act in var_act:
            event = Event({activity_key: act})
            trace.append(event)

    return trace


def get_activities_from_variant(variant, parameters=None):
    if parameters is None:
        parameters = {}

    return tuple(variant)


def get_variant_from_trace(trace, parameters=None):
    if parameters is None:
        parameters = {}

    activity_key = exec_utils.get_param_value(Parameters.ACTIVITY_KEY, parameters, xes_constants.DEFAULT_NAME_KEY)

    return tuple([x[activity_key] for x in trace])
