import math
import tempfile

import pydotplus


def get_corr_hex(num):
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
    left0 = graycolor / 16
    right0 = graycolor % 16

    left = get_corr_hex(left0)
    right = get_corr_hex(right0)

    return "#" + left + right + left + right + left + right


def apply(heu_net, parameters=None):
    if parameters is None:
        parameters = {}

    image_format = parameters["format"] if "format" in parameters else "png"

    graph = pydotplus.Dot()
    corr_nodes = {}
    corr_nodes_names = {}

    for node_name in heu_net.nodes:
        node = heu_net.nodes[node_name]
        node_occ = node.node_occ
        graycolor = transform_to_hex(max(255 - math.log(node_occ) * 9, 0))
        if node.node_type == "frequency":
            n = pydotplus.Node(name=node_name, shape="box", style="filled",
                               label=node_name + " (" + str(node_occ) + ")", fillcolor=graycolor)
        else:
            n = pydotplus.Node(name=node_name, shape="box", style="filled",
                               label=node_name, fillcolor=graycolor)
        corr_nodes[node] = n
        corr_nodes_names[node_name] = n
        graph.add_node(n)

    for node_name in heu_net.nodes:
        node = heu_net.nodes[node_name]
        for other_node in node.output_connections:
            if other_node in corr_nodes:
                for edge in node.output_connections[other_node]:
                    repr_value = str(edge.repr_value)
                    if edge.net_name:
                        e = pydotplus.Edge(src=corr_nodes[node], dst=corr_nodes[other_node],
                                           label=edge.net_name + " (" + repr_value + ")",
                                           color=edge.repr_color,
                                           fontcolor=edge.repr_color)
                    else:
                        e = pydotplus.Edge(src=corr_nodes[node], dst=corr_nodes[other_node], label=repr_value,
                                           color=edge.repr_color,
                                           fontcolor=edge.repr_color)

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
                    occ = heu_net.start_activities[index][node_name]
                    e = pydotplus.Edge(src=start_i, dst=sa, label=heu_net.net_name[index] + " (" + str(occ) + ")",
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
                    occ = heu_net.end_activities[index][node_name]
                    e = pydotplus.Edge(src=ea, dst=end_i, label=heu_net.net_name[index] + " (" + str(occ) + ")",
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
