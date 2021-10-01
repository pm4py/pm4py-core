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
from pm4py.objects.conversion.dfg.variants import to_petri_net_activity_defines_place, to_petri_net_invisibles_no_duplicates
from enum import Enum
from pm4py.util import exec_utils


class Variants(Enum):
    VERSION_TO_PETRI_NET_ACTIVITY_DEFINES_PLACE = to_petri_net_activity_defines_place
    VERSION_TO_PETRI_NET_INVISIBLES_NO_DUPLICATES = to_petri_net_invisibles_no_duplicates


DEFAULT_VARIANT = Variants.VERSION_TO_PETRI_NET_ACTIVITY_DEFINES_PLACE


def apply(dfg, parameters=None, variant=DEFAULT_VARIANT):
    return exec_utils.get_variant(variant).apply(dfg, parameters=parameters)
