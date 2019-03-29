import math
import tempfile

import pydotplus

from pm4py.visualization.common.utils import human_readable_stat


def get_corr_hex(num):
    """
    Gets correspondence between a number
    and an hexadecimal string

    Parameters
    -------------
    num
        Number

    Returns
    -------------
    hex_string
        Hexadecimal string
    """
    if num < 10:
        return str(int(num))
    elif num < 11:
        return "A"
    elif num < 12:
        return "B"
    elif num < 13:
        return "C"
    elif num < 14:
        return "D"
    elif num < 15:
        return "E"
    elif num < 16:
        return "F"


def transform_to_hex(graycolor):
    """
    Transform color to hexadecimal representation

    Parameters
    -------------
    graycolor
        Gray color (int from 0 to 255)

    Returns
    -------------
    hex_string
        Hexadecimal color
    """
    left0 = graycolor / 16
    right0 = graycolor % 16

    left00 = get_corr_hex(left0)
    right00 = get_corr_hex(right0)

    return "#" + left00 + right00 + left00 + right00 + left00 + right00


def apply(heu_net, parameters=None):
    """
    Gets a representation of an Heuristics Net

    Parameters
    -------------
    heu_net
        Heuristics net
    parameters
        Possible parameters of the algorithm, including: format

    Returns
    ------------
    gviz
        Representation of the Heuristics Net
    """
    if parameters is None:
        parameters = {}

    image_format = parameters["format"] if "format" in parameters else "png"

    graph = pydotplus.Dot()
    corr_nodes = {}
    corr_nodes_names = {}
    is_frequency = False

    for node_name in heu_net.nodes:
        node = heu_net.nodes[node_name]
        node_occ = node.node_occ
        graycolor = transform_to_hex(max(255 - math.log(node_occ) * 9, 0))
        if node.node_type == "frequency":
            is_frequency = True
            n = pydotplus.Node(name=node_name, shape="box", style="filled",
                               label=node_name + " (" + str(node_occ) + ")", fillcolor=graycolor)
        else:
            n = pydotplus.Node(name=node_name, shape="box", style="filled",
                               label=node_name, fillcolor=graycolor)
        corr_nodes[node] = n
        corr_nodes_names[node_name] = n
        graph.add_node(n)

    # gets max arc value
    max_arc_value = -1
    for node_name in heu_net.nodes:
        node = heu_net.nodes[node_name]
        for other_node in node.output_connections:
            if other_node in corr_nodes:
                for edge in node.output_connections[other_node]:
                    max_arc_value = max(max_arc_value, edge.repr_value)

    for node_name in heu_net.nodes:
        node = heu_net.nodes[node_name]
        for other_node in node.output_connections:
            if other_node in corr_nodes:
                for edge in node.output_connections[other_node]:
                    this_pen_width = 1.0 + math.log(1 + edge.repr_value) / 11.0
                    repr_value = str(edge.repr_value)
                    if edge.net_name:
                        if node.node_type == "frequency":
                            e = pydotplus.Edge(src=corr_nodes[node], dst=corr_nodes[other_node],
                                               label=edge.net_name + " (" + repr_value + ")",
                                               color=edge.repr_color,
                                               fontcolor=edge.repr_color, penwidth=this_pen_width)
                        else:
                            e = pydotplus.Edge(src=corr_nodes[node], dst=corr_nodes[other_node],
                                               label=edge.net_name + " (" + human_readable_stat(repr_value) + ")",
                                               color=edge.repr_color,
                                               fontcolor=edge.repr_color, penwidth=this_pen_width)
                    else:
                        if node.node_type == "frequency":
                            e = pydotplus.Edge(src=corr_nodes[node], dst=corr_nodes[other_node], label=repr_value,
                                               color=edge.repr_color,
                                               fontcolor=edge.repr_color, penwidth=this_pen_width)
                        else:
                            e = pydotplus.Edge(src=corr_nodes[node], dst=corr_nodes[other_node],
                                               label=human_readable_stat(repr_value),
                                               color=edge.repr_color,
                                               fontcolor=edge.repr_color, penwidth=this_pen_width)

                    graph.add_edge(e)

    for index, sa_list in enumerate(heu_net.start_activities):
        effective_sa_list = [n for n in sa_list if n in corr_nodes_names]
        if effective_sa_list:
            start_i = pydotplus.Node(name="start_" + str(index), label="", color=heu_net.default_edges_color[index],
                                     fillcolor=heu_net.default_edges_color[index], style="filled")
            graph.add_node(start_i)
            for node_name in effective_sa_list:
                sa = corr_nodes_names[node_name]
                if type(heu_net.start_activities[index]) is dict:
                    if is_frequency:
                        occ = heu_net.start_activities[index][node_name]
                        this_pen_width = 1.0 + math.log(1 + occ) / 11.0
                        if heu_net.net_name[index]:
                            e = pydotplus.Edge(src=start_i, dst=sa, label=heu_net.net_name[index] + " (" + str(occ) + ")",
                                               color=heu_net.default_edges_color[index],
                                               fontcolor=heu_net.default_edges_color[index], penwidth=this_pen_width)
                        else:
                            e = pydotplus.Edge(src=start_i, dst=sa, label=str(occ),
                                               color=heu_net.default_edges_color[index],
                                               fontcolor=heu_net.default_edges_color[index], penwidth=this_pen_width)
                    else:
                        e = pydotplus.Edge(src=start_i, dst=sa, label=heu_net.net_name[index],
                                           color=heu_net.default_edges_color[index],
                                           fontcolor=heu_net.default_edges_color[index])
                else:
                    e = pydotplus.Edge(src=start_i, dst=sa, label=heu_net.net_name[index],
                                       color=heu_net.default_edges_color[index],
                                       fontcolor=heu_net.default_edges_color[index])
                graph.add_edge(e)

    for index, ea_list in enumerate(heu_net.end_activities):
        effective_ea_list = [n for n in ea_list if n in corr_nodes_names]
        if effective_ea_list:
            end_i = pydotplus.Node(name="end_" + str(index), label="", color=heu_net.default_edges_color[index],
                                   fillcolor=heu_net.default_edges_color[index], style="filled")
            graph.add_node(end_i)
            for node_name in effective_ea_list:
                ea = corr_nodes_names[node_name]
                if type(heu_net.end_activities[index]) is dict:
                    if is_frequency:
                        occ = heu_net.end_activities[index][node_name]
                        this_pen_width = 1.0 + math.log(1 + occ) / 11.0
                        if heu_net.net_name[index]:
                            e = pydotplus.Edge(src=ea, dst=end_i, label=heu_net.net_name[index] + " (" + str(occ) + ")",
                                               color=heu_net.default_edges_color[index],
                                               fontcolor=heu_net.default_edges_color[index], penwidth=this_pen_width)
                        else:
                            e = pydotplus.Edge(src=ea, dst=end_i, label=str(occ),
                                               color=heu_net.default_edges_color[index],
                                               fontcolor=heu_net.default_edges_color[index], penwidth=this_pen_width)
                    else:
                        e = pydotplus.Edge(src=ea, dst=end_i, label=heu_net.net_name[index],
                                           color=heu_net.default_edges_color[index],
                                           fontcolor=heu_net.default_edges_color[index])
                else:
                    e = pydotplus.Edge(src=ea, dst=end_i, label=heu_net.net_name[index],
                                       color=heu_net.default_edges_color[index],
                                       fontcolor=heu_net.default_edges_color[index])
                graph.add_edge(e)

    file_name = tempfile.NamedTemporaryFile(suffix='.' + image_format)
    file_name.close()
    graph.write(file_name.name, format=image_format)
    return file_name
