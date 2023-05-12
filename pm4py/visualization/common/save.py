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
import shutil
import os
from pm4py.visualization.common import dot_util, html


def save(gviz, output_file_path, parameters=None):
    """
    Save the diagram

    Parameters
    -----------
    gviz
        GraphViz diagram
    output_file_path
        Path where the GraphViz output should be saved
    """
    format = os.path.splitext(output_file_path)[1][1:].lower()
    is_dot_installed = dot_util.check_dot_installed()

    if format.startswith("html"):
        html.save(gviz, output_file_path, parameters=parameters)
    else:
        render = gviz.render(cleanup=True)
        shutil.copyfile(render, output_file_path)
    """elif not is_dot_installed:
        raise Exception("impossible to save formats different from HTML without the Graphviz binary")"""

