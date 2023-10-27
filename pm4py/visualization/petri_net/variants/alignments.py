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
from pm4py.visualization.petri_net.common import visualize
from pm4py.visualization.petri_net.util import alignments_decoration
from pm4py.objects.petri_net.obj import PetriNet, Marking
from typing import Optional, Dict, Any


def apply(net: PetriNet, initial_marking: Marking, final_marking: Marking, log=None, aggregated_statistics=None, parameters: Optional[Dict[Any, Any]] = None) -> str:
    """
    Apply method for Petri net visualization (it calls the
    graphviz_visualization method)

    Parameters
    -----------
    net
        Petri net
    initial_marking
        Initial marking
    final_marking
        Final marking
    log
        (Optional) log
    aggregated_statistics
        Dictionary containing the frequency statistics
    parameters
        Algorithm parameters

    Returns
    -----------
    viz
        Graph object
    """
    if aggregated_statistics is None and log is not None:
        aggregated_statistics = alignments_decoration.get_alignments_decoration(net, initial_marking, final_marking,
                                                                                log=log)

    return visualize.apply(net, initial_marking, final_marking, parameters=parameters,
                           decorations=aggregated_statistics)
