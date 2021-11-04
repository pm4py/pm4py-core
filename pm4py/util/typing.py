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
from typing import Tuple, Dict, List, Any

TemporalProfile = Dict[Tuple[str, str], Tuple[float, float]]
TemporalProfileConformanceResults = List[List[Tuple[float, float, float, float]]]
TemporalProfileStreamingConfResults = Dict[str, List[Tuple[str, float, float, float, float]]]

AlignmentResult = Dict[str, Any]
ListAlignments = List[AlignmentResult]
