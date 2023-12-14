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
from enum import Enum, auto
from collections import Counter
from pm4py.algo.discovery.inductive.dtypes.im_ds import IMDataStructureUVCL


class FilteringType(Enum):
    DYNAMIC = auto()
    DECREASING_FACTOR = auto()


DEFAULT_FILTERING_TYPE = FilteringType.DECREASING_FACTOR
FILTERING_THRESHOLD = "filtering_threshold"
FILTERING_TYPE = "filtering_type"


def filter_most_frequent_variants(log):
    to_remove_freq = min([freq for var, freq in log.items()])
    new_log = Counter()
    for var, freq in log.items():
        if freq == to_remove_freq:
            continue
        new_log[var] = freq

    return IMDataStructureUVCL(new_log)


def filter_most_frequent_variants_with_decreasing_factor(log, decreasing_factor):
    sorted_variants = sorted(log, key=log.get, reverse=True)
    new_log = Counter()

    already_added_sum = 0
    prev_var_count = -1

    for variant in sorted_variants:
        frequency = log[variant]
        if already_added_sum == 0 or frequency > decreasing_factor * prev_var_count:
            new_log[variant] = frequency
            already_added_sum = already_added_sum + frequency
            prev_var_count = frequency
        else:
            break

    return IMDataStructureUVCL(new_log)
