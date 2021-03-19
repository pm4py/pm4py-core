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


class Outputs(Enum):
    OUTPUT_PLACES_INTERVAL_TREES = "places_interval_trees"
    OUTPUT_TRANSITIONS_INTERVAL_TREES = "transitions_interval_trees"
    OUTPUT_CASES_EX_TIME = "cases_ex_time"
    OUTPUT_MEDIAN_CASES_EX_TIME = "median_cases_ex_time"
    OUTPUT_CASE_ARRIVAL_RATIO = "input_case_arrival_ratio"
    OUTPUT_TOTAL_CASES_TIME = "total_cases_time"
