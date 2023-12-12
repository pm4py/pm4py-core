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
from pm4py.visualization.align_table.variants import classic
from pm4py.visualization.common import gview
from pm4py.visualization.common import save as gsave
from pm4py.visualization.common.gview import serialize, serialize_dot
from enum import Enum
from pm4py.util import exec_utils
from typing import Optional, Dict, Any, Union
from pm4py.objects.log.obj import EventLog
from pm4py.util import typing
import graphviz
from pm4py.objects.conversion.log import converter as log_converter
import pandas as pd

class Variants(Enum):
    CLASSIC = classic


DEFAULT_VARIANT = Variants.CLASSIC


def apply(log: Union[EventLog, pd.DataFrame], aligned_traces: typing.ListAlignments, variant=DEFAULT_VARIANT, parameters: Optional[Dict[Any, Any]] = None) -> graphviz.Source:
    """
    Gets the alignment table visualization from the alignments output

    Parameters
    -------------
    log
        Event log
    aligned_traces
        Aligned traces
    variant
        Variant of the algorithm to apply, possible values:
            - Variants.CLASSIC
    parameters
        Parameters of the algorithm

    Returns
    -------------
    gviz
        Graphviz object
    """
    log = log_converter.apply(log, variant=log_converter.Variants.TO_EVENT_LOG, parameters=parameters)
    return exec_utils.get_variant(variant).apply(log, aligned_traces, parameters=parameters)


def save(gviz: graphviz.Digraph, output_file_path: str, parameters=None):
    """
    Save the diagram

    Parameters
    -----------
    gviz
        GraphViz diagram
    output_file_path
        Path where the GraphViz output should be saved
    """
    gsave.save(gviz, output_file_path, parameters=parameters)
    return ""


def view(gviz: graphviz.Digraph, parameters=None):
    """
    View the diagram

    Parameters
    -----------
    gviz
        GraphViz diagram
    """
    return gview.view(gviz, parameters=parameters)


def matplotlib_view(gviz: graphviz.Digraph, parameters=None):
    """
    Views the diagram using Matplotlib

    Parameters
    ---------------
    gviz
        Graphviz
    """

    return gview.matplotlib_view(gviz, parameters=parameters)
