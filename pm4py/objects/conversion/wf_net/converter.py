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

from pm4py.objects.conversion.wf_net.variants import to_process_tree, to_bpmn
from pm4py.util import exec_utils


class Variants(Enum):
    TO_PROCESS_TREE = to_process_tree
    TO_BPMN = to_bpmn


DEFAULT_VARIANT = Variants.TO_PROCESS_TREE


def apply(net, im, fm, variant=DEFAULT_VARIANT, parameters=None):
    return exec_utils.get_variant(variant).apply(net, im, fm, parameters=parameters)
