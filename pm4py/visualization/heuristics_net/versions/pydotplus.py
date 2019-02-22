import tempfile

import pydotplus


def apply(heu_net, parameters=None):
    if parameters is None:
        parameters = {}

    image_format = parameters["format"] if "format" in parameters else "png"

    graph = pydotplus.Dot()
    corr_nodes = {}
    corr_nodes_names = {}

    for node_name in heu_net.nodes:
        node = heu_net.nodes[node_name]
        n = pydotplus.Node(name=node_name, shape="box", style="rounded",
                           label=node_name)
        corr_nodes[node] = n
        corr_nodes_names[node_name] = n
        graph.add_node(n)

    for node_name in heu_net.nodes:
        node = heu_net.nodes[node_name]
        for other_node in node.output_connections:
            if other_node in corr_nodes:
                for edge in node.output_connections[other_node]:
                    e = pydotplus.Edge(src=corr_nodes[node], dst=corr_nodes[other_node], label=str(edge.repr_value),
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
                e = pydotplus.Edge(src=ea, dst=end_i, label=heu_net.net_name[index],
                                   color=heu_net.default_edges_color[index],
                                   fontcolor=heu_net.default_edges_color[index])
                graph.add_edge(e)

    file_name = tempfile.NamedTemporaryFile(suffix='.' + image_format)
    file_name.close()
    graph.write(file_name.name, format=image_format)
    return file_name
