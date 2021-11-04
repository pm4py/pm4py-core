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
import pkgutil

if pkgutil.find_loader("graphviz"):
    # imports the visualizations only if graphviz is installed
    from pm4py.visualization import common, dfg, petri_net, process_tree, transition_system, align_table, \
        footprints, bpmn, trie, dotted_chart
    if pkgutil.find_loader("matplotlib") and pkgutil.find_loader("pyvis"):
        # SNA requires both packages matplotlib and pyvis. These are included in the default installation;
        # however, they may lead to problems in some platforms/deployments
        from pm4py.visualization import sna, performance_spectrum
    if pkgutil.find_loader("pydotplus"):
        # heuristics net visualization requires pydotplus. This is included in the default installation;
        # however, they may lead to problems in some platforms/deployments
        from pm4py.visualization import heuristics_net
    if pkgutil.find_loader("sklearn"):
        from pm4py.visualization import decisiontree

if pkgutil.find_loader("matplotlib"):
    # graphs require matplotlib. This is included in the default installation;
    # however, they may lead to problems in some platforms/deployments
    from pm4py.visualization import graphs
