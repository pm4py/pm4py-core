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
from graphviz import Source
import tempfile

from pm4py.statistics.variants.log import get as variants_get
from pm4py.util import exec_utils
from enum import Enum
from typing import Optional, Dict, Any
from pm4py.objects.log.obj import EventLog
from pm4py.util import typing
import graphviz


class Parameters(Enum):
    FORMAT = "format"


def apply(log: EventLog, aligned_traces: typing.ListAlignments, parameters: Optional[Dict[Any, Any]] = None) -> graphviz.Source:
    """
    Gets the alignment table visualization from the alignments output

    Parameters
    -------------
    log
        Event log
    aligned_traces
        Aligned traces
    parameters
        Parameters of the algorithm

    Returns
    -------------
    gviz
        Graphviz object
    """
    if parameters is None:
        parameters = {}

    variants_idx_dict = variants_get.get_variants_from_log_trace_idx(log, parameters=parameters)

    variants_idx_list = []
    for variant in variants_idx_dict:
        variants_idx_list.append((variant, variants_idx_dict[variant]))
    variants_idx_list = sorted(variants_idx_list, key=lambda x: len(x[1]), reverse=True)

    image_format = exec_utils.get_param_value(Parameters.FORMAT, parameters, "png")

    table_alignments_list = ["digraph {\n", "tbl [\n", "shape=plaintext\n", "label=<\n"]
    table_alignments_list.append("<table border='0' cellborder='1' color='blue' cellspacing='0'>\n")

    table_alignments_list.append("<tr><td>Variant</td><td>Alignment</td></tr>\n")

    for index, variant in enumerate(variants_idx_list):
        al_tr = aligned_traces[variant[1][0]]
        table_alignments_list.append("<tr>")
        table_alignments_list.append(
            "<td><font point-size='9'>Variant " + str(index + 1) + " (" + str(
                len(variant[1])) + " occurrences)</font></td>")
        table_alignments_list.append("<td><font point-size='6'><table border='0'><tr>")
        for move in al_tr['alignment']:
            if not (move[0] == ">>" or move[1] == ">>"):
                # sync move
                table_alignments_list.append("<td bgcolor=\"lightgreen\">" + str(move[1]).replace(">", "&gt;") + "</td>")
            elif move[1] == ">>":
                # move on log
                table_alignments_list.append("<td bgcolor=\"orange\"><b>(LM)</b>" + str(move[0]).replace(">", "&gt;") + "</td>")
            elif move[0] == ">>":
                # move on model
                table_alignments_list.append("<td bgcolor=\"violet\"><b>(MM)</b>" + str(move[1]).replace(">", "&gt;") + "</td>")
        table_alignments_list.append("</tr></table></font></td>")
        table_alignments_list.append("</tr>")

    table_alignments_list.append("</table>\n")
    table_alignments_list.append(">];\n")
    table_alignments_list.append("}\n")

    table_alignments = "".join(table_alignments_list)

    filename = tempfile.NamedTemporaryFile(suffix='.gv')
    filename.close()

    gviz = Source(table_alignments, filename=filename.name)
    gviz.format = image_format

    return gviz
