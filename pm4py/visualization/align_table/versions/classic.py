from graphviz import Source
from pm4py.algo.filtering.log.variants import variants_filter

def apply(log, aligned_traces, parameters=None):
    if parameters is None:
        parameters = {}

    variants_idx_dict = variants_filter.get_variants_from_log_trace_idx(log, parameters=parameters)

    variants_idx_list = []
    for variant in variants_idx_dict:
        variants_idx_list.append((variant, variants_idx_dict[variant]))
    variants_idx_list = sorted(variants_idx_list, key=lambda x: len(x[1]), reverse=True)

    image_format = parameters["format"] if "format" in parameters else "png"

    table_alignments_list = ["digraph {\n","tbl [\n","shape=plaintext\n","label=<\n"]
    table_alignments_list.append("<table border='0' cellborder='1' color='blue' cellspacing='0'>\n")

    table_alignments_list.append("<tr><td>Variant</td><td>Alignment</td></tr>\n")

    for index, variant in enumerate(variants_idx_list):
        al_tr = aligned_traces[variant[1][0]]
        table_alignments_list.append("<tr>")
        table_alignments_list.append("<td>Variant "+str(index+1)+" ("+str(len(variant[1]))+" occurrences)<br />"+variant[0]+"</td>")
        table_alignments_list.append("<td><table border='0'><tr>")
        for move in al_tr['alignment']:
            move_descr = str(move[1]).replace(">","&gt;")
            table_alignments_list.append("<td>"+move_descr+"</td>")
        table_alignments_list.append("</tr></table></td>")
        table_alignments_list.append("</tr>")

    table_alignments_list.append("</table>\n")
    table_alignments_list.append(">];\n")
    table_alignments_list.append("}\n")

    table_alignments = "".join(table_alignments_list)

    gviz = Source(table_alignments)
    gviz.format = image_format

    return gviz
