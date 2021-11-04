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

warnings.warn('please use the pm4py.objects.petri_net package instead.')

import pkgutil

from pm4py.objects.petri import common, incidence_matrix, obj, \
    reachability_graph, semantics, synchronous_product, utils, check_soundness, networkx_graph, align_utils, \
    explore_path, performance_map, embed_stochastic_map, reduction

if pkgutil.find_loader("lxml"):
    from pm4py.objects.petri import exporter, importer
