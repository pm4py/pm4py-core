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
from enum import Enum

from pm4py.objects.conversion.log.variants import to_event_stream, to_event_log, to_data_frame, to_nx


class Variants(Enum):
    TO_EVENT_LOG = to_event_log
    TO_EVENT_STREAM = to_event_stream
    TO_DATA_FRAME = to_data_frame
    TO_NX = to_nx


TO_EVENT_LOG = Variants.TO_EVENT_LOG
TO_EVENT_STREAM = Variants.TO_EVENT_STREAM
TO_DATA_FRAME = Variants.TO_DATA_FRAME


def apply(log, parameters=None, variant=None):
    if variant is None:
        variant = Variants.TO_EVENT_LOG
    return variant.value.apply(log, parameters=parameters)
