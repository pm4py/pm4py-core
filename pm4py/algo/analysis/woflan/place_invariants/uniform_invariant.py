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
from pm4py.algo.analysis.woflan.place_invariants.place_invariants import compute_place_invariants
from pm4py.algo.analysis.woflan.place_invariants.utility import transform_basis


def apply(net):
    place_invariants= compute_place_invariants(net)
    modified_invariants=transform_basis(place_invariants, style='uniform')
    return modified_invariants

