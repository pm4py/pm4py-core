from graphviz import Source
import tempfile

from pm4py.statistics.variants.log import get as variants_get


def apply(log, aligned_traces, parameters=None):
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

    image_format = parameters["format"] if "format" in parameters else "png"

    table_alignments_list = ["digraph {\n", "tbl [\n", "shape=plaintext\n", "label=<\n"]
    table_alignments_list.append("<table border='0' cellborder='1' color='blue' cellspacing='0'>\n")

    table_alignments_list.append("<tr><td>Variant</td><td>Alignment</td></tr>\n")

    for index, variant in enumerate(variants_idx_list):
        al_tr = aligned_traces[variant[1][0]]
        table_alignments_list.append("<tr>")
        table_alignments_list.append(
            "<td><font point-size='9'>Variant " + str(index + 1) + " (" + str(len(variant[1])) + " occurrences)</font></td>")
        table_alignments_list.append("<td><font point-size='6'><table border='0'><tr>")
        for move in al_tr['alignment']:
            move_descr = str(move[1]).replace(">", "&gt;")
            if not move[0][0] == ">>" or move[0][1] == ">>":
                table_alignments_list.append("<td bgcolor=\"green\">" + move_descr + "</td>")
            elif move[0][1] == ">>":
                table_alignments_list.append("<td bgcolor=\"violet\">" + move_descr + "</td>")
            elif move[0][0] == ">>":
                table_alignments_list.append("<td bgcolor=\"gray\">" + move_descr + "</td>")
        table_alignments_list.append("</tr></table></font></td>")
        table_alignments_list.append("</tr>")

    table_alignments_list.append("</table>\n")
    table_alignments_list.append(">];\n")
    table_alignments_list.append("}\n")

    table_alignments = "".join(table_alignments_list)

    filename = tempfile.NamedTemporaryFile(suffix='.gv')

    gviz = Source(table_alignments, filename=filename.name)
    gviz.format = image_format

    return gviz
