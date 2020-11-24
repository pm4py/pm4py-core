from collections import Counter
from copy import deepcopy
from enum import Enum

from pm4py.objects.bpmn.bpmn_graph import BPMN
from pm4py.util import exec_utils


class EndpointDirection(Enum):
    RIGHT = "right"
    LEFT = "left"
    TOP = "top"
    BOTTOM = "bottom"


class Parameters(Enum):
    FOCUS = "focus"
    SCALING_FACT_X = "scaling_fact_x"
    SCALING_FACT_Y = "scaling_fact_y"
    TASK_WH = "task_wh"


def get_right_edge_coord(node, p, partial_counter, total_counter):
    y_factor = partial_counter[EndpointDirection.RIGHT] / (total_counter[EndpointDirection.RIGHT] + 1.0)
    new_x = p[0] + node.get_width()
    new_y = p[1] + round(
        node.get_height() * y_factor)
    return (new_x, new_y)


def get_left_edge_coord(node, p, partial_counter, total_counter):
    y_factor = partial_counter[EndpointDirection.LEFT] / (total_counter[EndpointDirection.LEFT] + 1.0)
    new_x = p[0]
    new_y = p[1] + round(
        node.get_height() * y_factor)
    return (new_x, new_y)


def get_top_edge_coord(node, p, partial_counter, total_counter):
    x_factor = partial_counter[EndpointDirection.TOP] / (total_counter[EndpointDirection.TOP] + 1.0)
    new_x = p[0] + round(node.get_width() * x_factor)
    new_y = p[1]
    return (new_x, new_y)


def get_bottom_edge_coord(node, p, partial_counter, total_counter):
    x_factor = partial_counter[EndpointDirection.BOTTOM] / (total_counter[EndpointDirection.BOTTOM] + 1.0)
    new_x = p[0] + round(node.get_width() * x_factor)
    new_y = p[1] + node.get_height()
    return (new_x, new_y)


def bfs_bpmn(nodes, edges):
    start_nodes = [n for n in nodes if isinstance(n, BPMN.StartEvent)]
    level = 0
    bfs = {n: level for n in start_nodes}
    while True:
        level += 1
        to_visit = list(e[1] for e in edges if e[0] in bfs and e[1] not in bfs and not isinstance(e[1], BPMN.EndEvent))
        if not to_visit:
            break
        for n in to_visit:
            bfs[n] = level
    other_nodes = [n for n in nodes if n not in bfs]
    level += 1
    for n in other_nodes:
        bfs[n] = level
    return bfs


def sort_nodes_given_bfs(nodes, bfs):
    something_changed = True
    while something_changed:
        something_changed = False
        i = 0
        while i < len(nodes):
            name_i = nodes[i].get_name()
            j = i + 1
            while j < len(nodes):
                name_j = nodes[j].get_name()
                should_exchange = False
                if bfs[nodes[i]] > bfs[nodes[j]]:
                    should_exchange = True
                elif bfs[nodes[i]] == bfs[nodes[j]] and name_j and not name_i:
                    should_exchange = True
                elif bfs[nodes[i]] == bfs[nodes[j]] and name_i and name_j and name_i <= name_j:
                    should_exchange = True
                if should_exchange:
                    nodes[i], nodes[j] = nodes[j], nodes[i]
                    something_changed = True
                    break
                j = j + 1
            i = i + 1
    return nodes


def sort_edges_given_bfs(edges, bfs):
    something_changed = True
    while something_changed:
        something_changed = False
        i = 0
        while i < len(edges):
            j = i + 1
            while j < len(edges):
                should_exchange = False
                if bfs[edges[i][0]] > bfs[edges[j][0]]:
                    should_exchange = True
                elif bfs[edges[i][0]] == bfs[edges[j][0]] and bfs[edges[i][1]] > bfs[edges[j][1]]:
                    should_exchange = True
                if should_exchange:
                    edges[i], edges[j] = edges[j], edges[i]
                    something_changed = True
                    break
                j = j + 1
            i = i + 1
    return edges


def apply(bpmn_graph, parameters=None):
    """
    Layouts a BPMN graph (inserting the positions of the nodes and the layouting of the edges)

    Parameters
    -------------
    bpmn_graph
        BPMN graph
    parameters
        Parameters of the algorithm

    Returns
    -------------
    bpmn_graph
        BPMN graph with layout information
    """
    if parameters is None:
        parameters = {}

    try:
        import pygraphviz
    except ImportError:
        raise ImportError('missing pygraphviz: ',
                          'http://pygraphviz.github.io/')

    nodes = bpmn_graph.get_nodes()
    flows = bpmn_graph.get_flows()
    graph = bpmn_graph.get_graph()

    # convert nx graph to pygraphviz graph
    A = pygraphviz.AGraph(name=bpmn_graph.get_name(), strict=True, directed=True, rankdir="LR")

    # assure an ordering as-constant-as-possible is provided to the DOT engine
    graph_nodes = list(graph.nodes(data=False))
    graph_edges = list(graph.edges(data=False))
    bfs = bfs_bpmn(graph_nodes, graph_edges)
    graph_nodes = sort_nodes_given_bfs(graph_nodes, bfs)
    graph_edges = sort_edges_given_bfs(graph_edges, bfs)

    for n in graph_nodes:
        A.add_node(n)

    for tup in graph_edges:
        A.add_edge(tup[0], tup[1])

    # use built-in layout function from pygraphviz
    A.layout(prog="dot")

    focus = exec_utils.get_param_value(Parameters.FOCUS, parameters, 0.42)
    scaling_fact_x = exec_utils.get_param_value(Parameters.SCALING_FACT_X, parameters, 320.0) * focus
    scaling_fact_y = exec_utils.get_param_value(Parameters.SCALING_FACT_Y, parameters, 150.0) * focus
    task_wh = exec_utils.get_param_value(Parameters.TASK_WH, parameters, 60)

    # add node positions to BPMN nodes
    for n in graph_nodes:
        node = pygraphviz.Node(A, n)
        xs = node.attr["pos"].split(',')
        node_pos = tuple(float(x) for x in xs)
        # width = round(100.0 * float(node.attr["width"]) / 7.0)
        n.set_x(int(node_pos[0]))
        n.set_y(int(node_pos[1]))
        n.set_height(task_wh)
        if isinstance(n, BPMN.Task):
            this_width = min(round(2 * task_wh), round(2 * (len(n.get_name()) + 7) * task_wh / 22.0))
            n.set_width(this_width)
        else:
            n.set_width(task_wh)

    # stretch BPMN a bit, cause y coordinates are ususally pretty small compared to x
    max_node_x = max(node.get_x() for node in nodes)
    max_node_y = max(node.get_y() for node in nodes)
    different_x = len(set(node.get_x() for node in nodes))
    different_y = len(set(node.get_y() for node in nodes))

    stretch_fact_x = scaling_fact_x * different_x / max_node_x
    stretch_fact_y = scaling_fact_y * different_y / max_node_y

    for node in nodes:
        node.set_x(round(node.get_x() * stretch_fact_x))
        node.set_y(round(node.get_y() * stretch_fact_y))

    outgoing_edges = dict()
    ingoing_edges = dict()
    sources_dict = dict()
    targets_dict = dict()

    for flow in flows:
        source = flow.get_source()
        target = flow.get_target()

        x_src = source.get_x()
        x_trg = target.get_x()
        y_src = source.get_y()
        y_trg = target.get_y()

        sources_dict[(x_src, y_src)] = source
        targets_dict[(x_trg, y_trg)] = target

        diff_x = abs(x_trg - x_src)
        diff_y = abs(y_src - y_trg)

        if not (x_src, y_src) in outgoing_edges:
            outgoing_edges[(x_src, y_src)] = {}
        outgoing_edges[(x_src, y_src)][(x_trg, y_trg)] = {EndpointDirection.RIGHT: 0.0, EndpointDirection.LEFT: 0.0,
                                                          EndpointDirection.TOP: 0.0, EndpointDirection.BOTTOM: 0.0}
        if not (x_trg, y_trg) in ingoing_edges:
            ingoing_edges[(x_trg, y_trg)] = {}
        ingoing_edges[(x_trg, y_trg)][(x_src, y_src)] = {EndpointDirection.RIGHT: 0.0, EndpointDirection.LEFT: 0.0,
                                                         EndpointDirection.TOP: 0.0, EndpointDirection.BOTTOM: 0.0}

        if x_trg > x_src:
            outgoing_edges[(x_src, y_src)][(x_trg, y_trg)][EndpointDirection.RIGHT] = diff_x / (diff_x + diff_y)
            ingoing_edges[(x_trg, y_trg)][(x_src, y_src)][EndpointDirection.LEFT] = diff_x / (diff_x + diff_y)
        else:
            outgoing_edges[(x_src, y_src)][(x_trg, y_trg)][EndpointDirection.LEFT] = diff_x / (diff_x + diff_y)
            ingoing_edges[(x_trg, y_trg)][(x_src, y_src)][EndpointDirection.RIGHT] = diff_x / (diff_x + diff_y)

        if y_src > y_trg:
            outgoing_edges[(x_src, y_src)][(x_trg, y_trg)][EndpointDirection.TOP] = diff_y / (diff_x + diff_y)
            ingoing_edges[(x_trg, y_trg)][(x_src, y_src)][EndpointDirection.BOTTOM] = diff_y / (diff_x + diff_y)
        else:
            outgoing_edges[(x_src, y_src)][(x_trg, y_trg)][EndpointDirection.BOTTOM] = diff_y / (diff_x + diff_y)
            ingoing_edges[(x_trg, y_trg)][(x_src, y_src)][EndpointDirection.TOP] = diff_y / (diff_x + diff_y)

    # normalization
    outgoing_edges0 = deepcopy(outgoing_edges)
    ingoing_edges0 = deepcopy(ingoing_edges)

    for p1 in outgoing_edges:
        sum_right = 0.0
        sum_left = 0.0
        sum_top = 0.0
        sum_bottom = 0.0
        for p2 in outgoing_edges[p1]:
            sum_right += outgoing_edges0[p1][p2][EndpointDirection.RIGHT]
            sum_left += outgoing_edges0[p1][p2][EndpointDirection.LEFT]
            sum_top += outgoing_edges0[p1][p2][EndpointDirection.TOP]
            sum_bottom += outgoing_edges0[p1][p2][EndpointDirection.BOTTOM]
        if p1 in ingoing_edges:
            for p2 in ingoing_edges[p1]:
                sum_right += ingoing_edges0[p1][p2][EndpointDirection.RIGHT]
                sum_left += ingoing_edges0[p1][p2][EndpointDirection.LEFT]
                sum_top += ingoing_edges0[p1][p2][EndpointDirection.TOP]
                sum_bottom += ingoing_edges0[p1][p2][EndpointDirection.BOTTOM]
        for p2 in outgoing_edges[p1]:
            if sum_right > 0:
                outgoing_edges[p1][p2][EndpointDirection.RIGHT] = outgoing_edges[p1][p2][
                                                                      EndpointDirection.RIGHT] ** 2 / sum_right
            if sum_left > 0:
                outgoing_edges[p1][p2][EndpointDirection.LEFT] = outgoing_edges[p1][p2][
                                                                     EndpointDirection.LEFT] ** 2 / sum_left
            if sum_top > 0:
                outgoing_edges[p1][p2][EndpointDirection.TOP] = outgoing_edges[p1][p2][
                                                                    EndpointDirection.TOP] ** 2 / sum_top
            if sum_bottom > 0:
                outgoing_edges[p1][p2][EndpointDirection.BOTTOM] = outgoing_edges[p1][p2][
                                                                       EndpointDirection.BOTTOM] ** 2 / sum_bottom
    for p1 in ingoing_edges:
        sum_right = 0.0
        sum_left = 0.0
        sum_top = 0.0
        sum_bottom = 0.0
        for p2 in ingoing_edges[p1]:
            sum_right += ingoing_edges0[p1][p2][EndpointDirection.RIGHT]
            sum_left += ingoing_edges0[p1][p2][EndpointDirection.LEFT]
            sum_top += ingoing_edges0[p1][p2][EndpointDirection.TOP]
            sum_bottom += ingoing_edges0[p1][p2][EndpointDirection.BOTTOM]
        if p1 in outgoing_edges:
            for p2 in outgoing_edges[p1]:
                sum_right += outgoing_edges0[p1][p2][EndpointDirection.RIGHT]
                sum_left += outgoing_edges0[p1][p2][EndpointDirection.LEFT]
                sum_top += outgoing_edges0[p1][p2][EndpointDirection.TOP]
                sum_bottom += outgoing_edges0[p1][p2][EndpointDirection.BOTTOM]
        for p2 in ingoing_edges[p1]:
            if sum_right > 0:
                ingoing_edges[p1][p2][EndpointDirection.RIGHT] = ingoing_edges[p1][p2][
                                                                     EndpointDirection.RIGHT] ** 2 / sum_right
            if sum_left > 0:
                ingoing_edges[p1][p2][EndpointDirection.LEFT] = ingoing_edges[p1][p2][
                                                                    EndpointDirection.LEFT] ** 2 / sum_left
            if sum_top > 0:
                ingoing_edges[p1][p2][EndpointDirection.TOP] = ingoing_edges[p1][p2][
                                                                   EndpointDirection.TOP] ** 2 / sum_top
            if sum_bottom > 0:
                ingoing_edges[p1][p2][EndpointDirection.BOTTOM] = ingoing_edges[p1][p2][
                                                                      EndpointDirection.BOTTOM] ** 2 / sum_bottom

    # keep best direction
    for p1 in outgoing_edges:
        for p2 in outgoing_edges[p1]:
            vals = sorted([(x, y) for x, y in outgoing_edges[p1][p2].items()], key=lambda x: x[1], reverse=True)
            outgoing_edges[p1][p2] = vals[0][0]
    for p1 in ingoing_edges:
        for p2 in ingoing_edges[p1]:
            vals = sorted([(x, y) for x, y in ingoing_edges[p1][p2].items()], key=lambda x: x[1], reverse=True)
            ingoing_edges[p1][p2] = vals[0][0]

    total_counter = dict()
    partial_counter = dict()
    for p1 in outgoing_edges:
        if p1 not in total_counter:
            total_counter[p1] = Counter()
        for p2 in outgoing_edges[p1]:
            dir = outgoing_edges[p1][p2]
            total_counter[p1][dir] += 1
    for p1 in ingoing_edges:
        if p1 not in total_counter:
            total_counter[p1] = Counter()
        for p2 in ingoing_edges[p1]:
            dir = ingoing_edges[p1][p2]
            total_counter[p1][dir] += 1

    outgoing_edges_dirs = deepcopy(outgoing_edges)
    ingoing_edges_dirs = deepcopy(ingoing_edges)

    # decide exiting/entering point for edges
    for p1 in outgoing_edges:
        node = sources_dict[p1]
        if p1 not in partial_counter:
            partial_counter[p1] = Counter()
        sorted_outgoing_edges = sorted(outgoing_edges[p1], key=lambda x: x, reverse=False)
        for p2 in sorted_outgoing_edges:
            dir = outgoing_edges[p1][p2]
            partial_counter[p1][dir] += 1
            if dir == EndpointDirection.RIGHT:
                outgoing_edges[p1][p2] = get_right_edge_coord(node, p1, partial_counter[p1], total_counter[p1])
            elif dir == EndpointDirection.LEFT:
                outgoing_edges[p1][p2] = get_left_edge_coord(node, p1, partial_counter[p1], total_counter[p1])
            elif dir == EndpointDirection.TOP:
                outgoing_edges[p1][p2] = get_top_edge_coord(node, p1, partial_counter[p1], total_counter[p1])
            elif dir == EndpointDirection.BOTTOM:
                outgoing_edges[p1][p2] = get_bottom_edge_coord(node, p1, partial_counter[p1], total_counter[p1])
    for p1 in ingoing_edges:
        node = targets_dict[p1]
        if p1 not in partial_counter:
            partial_counter[p1] = Counter()
        sorted_ingoing_edges = sorted(ingoing_edges[p1], key=lambda x: x, reverse=False)
        for p2 in sorted_ingoing_edges:
            dir = ingoing_edges[p1][p2]
            partial_counter[p1][dir] += 1
            if dir == EndpointDirection.RIGHT:
                ingoing_edges[p1][p2] = get_right_edge_coord(node, p1, partial_counter[p1], total_counter[p1])
            elif dir == EndpointDirection.LEFT:
                ingoing_edges[p1][p2] = get_left_edge_coord(node, p1, partial_counter[p1], total_counter[p1])
            elif dir == EndpointDirection.TOP:
                ingoing_edges[p1][p2] = get_top_edge_coord(node, p1, partial_counter[p1], total_counter[p1])
            elif dir == EndpointDirection.BOTTOM:
                ingoing_edges[p1][p2] = get_bottom_edge_coord(node, p1, partial_counter[p1], total_counter[p1])

    # order the left-entering ingoing edges better
    for p1 in ingoing_edges:
        vals = [(x, y) for x, y in ingoing_edges[p1].items() if y[0] == p1[0]]
        if len(vals) > 1:
            vals_x = [x[0] for x in vals]
            vals_y = [x[1] for x in vals]
            vals_x = sorted(vals_x)
            vals_y = sorted(vals_y)
            for i in range(len(vals_x)):
                ingoing_edges[p1][vals_x[i]] = vals_y[i]

    # set waypoints for edges
    for flow in flows:
        source = flow.get_source()
        target = flow.get_target()

        flow.del_waypoints()

        x_src = source.get_x()
        x_trg = target.get_x()
        y_src = source.get_y()
        y_trg = target.get_y()
        p1 = (x_src, y_src)
        p2 = (x_trg, y_trg)

        source_x = outgoing_edges[p1][p2][0]
        source_y = outgoing_edges[p1][p2][1]
        target_x = ingoing_edges[p2][p1][0]
        target_y = ingoing_edges[p2][p1][1]
        dir_source = outgoing_edges_dirs[p1][p2]
        dir_target = ingoing_edges_dirs[p2][p1]

        middle_x = (source_x + target_x) / 2.0
        middle_y = (source_y + target_y) / 2.0

        flow.add_waypoint((source_x, source_y))
        if dir_source in [EndpointDirection.LEFT, EndpointDirection.RIGHT]:
            if dir_target in [EndpointDirection.LEFT, EndpointDirection.RIGHT]:
                flow.add_waypoint((middle_x, source_y))
                flow.add_waypoint((middle_x, target_y))
            elif dir_target in [EndpointDirection.TOP, EndpointDirection.BOTTOM]:
                flow.add_waypoint((target_x, source_y))
        elif dir_source in [EndpointDirection.TOP, EndpointDirection.BOTTOM]:
            if dir_target in [EndpointDirection.TOP, EndpointDirection.BOTTOM]:
                flow.add_waypoint((source_x, middle_y))
                flow.add_waypoint((target_x, middle_y))
            elif dir_target in [EndpointDirection.LEFT, EndpointDirection.RIGHT]:
                flow.add_waypoint((source_x, target_y))

        flow.add_waypoint((target_x, target_y))

    return bpmn_graph
