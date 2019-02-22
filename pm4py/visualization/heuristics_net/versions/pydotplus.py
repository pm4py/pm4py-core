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
            e = pydotplus.Edge(src=corr_nodes[node], dst=corr_nodes[other_node], label="")
            graph.add_edge(e)

    file_name = tempfile.NamedTemporaryFile(suffix='.' + image_format)
    file_name.close()
    graph.write(file_name.name, format=image_format)
    return file_name
