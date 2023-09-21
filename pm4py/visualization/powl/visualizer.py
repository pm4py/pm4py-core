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

from pm4py.visualization.common import gview
from pm4py.visualization.common import save as gsave
from pm4py.visualization.powl.variants import basic
from enum import Enum
from pm4py.util import exec_utils
from typing import Optional, Dict, Any
from pm4py.objects.powl.obj import POWL
import graphviz


class Variants(Enum):
    BASIC = basic


DEFAULT_VARIANT = Variants.BASIC


def apply(powl: POWL, parameters: Optional[Dict[Any, Any]] = None, variant=DEFAULT_VARIANT) -> graphviz.Graph:
    """
    Method for POWL model representation

    Parameters
    -----------
    powl
        POWL model
    parameters
        Possible parameters of the algorithm:
            Parameters.FORMAT -> Format of the image (PDF, PNG, SVG; default PNG)
    variant
        Variant of the algorithm to use:
            - Variants.BASIC

    Returns
    -----------
    gviz
        GraphViz object
    """
    return exec_utils.get_variant(variant).apply(powl, parameters=parameters)


def save(gviz: graphviz.Graph, output_file_path: str):
    """
    Save the diagram

    Parameters
    -----------
    gviz
        GraphViz diagram
    output_file_path
        Path where the GraphViz output should be saved
    """
    gsave.save(gviz, output_file_path)


def view(gviz: graphviz.Graph):
    """
    View the diagram

    Parameters
    -----------
    gviz
        GraphViz diagram
    """
    return gview.view(gviz)


def matplotlib_view(gviz: graphviz.Graph):
    """
    Views the diagram using Matplotlib

    Parameters
    ---------------
    gviz
        Graphviz
    """

    return gview.matplotlib_view(gviz)
