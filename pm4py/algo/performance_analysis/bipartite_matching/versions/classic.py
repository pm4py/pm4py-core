import networkx as nx
from ortools.linear_solver import pywraplp
from pm4py.algo.performance_analysis.bipartite_matching.util import helper
from pm4py.algo.performance_analysis.bipartite_matching.util import filtering
import pm4py.algo.performance_analysis.bipartite_matching.util.shared_variables as sv


def apply(log, start, end, classifier="concept:name"):
    """
    Measure the duration of a log

    Parameters
    ------------
    log
        Event log
    start
        Start activities
    end
        End activities
    classifier
        Event classifier (activity name by default)
    Returns
    ------------
    result
        Case ID: (edges selected, statistical result)
    """

    sv.set_log(log)
    sv.set_classifier(classifier)

    log_cleaned = helper.select_attributes(sv.log, sv.classifier)
    sv.set_indexed_log(helper.index_event(log_cleaned))

    return update(start, end)


def update(start, end):
    """
    Update the performance analysis depending on user inputs

    Parameters
    ------------
    start
        Start activities
    end
        End activities
    Returns
    ------------
    result
        Case ID: (edges selected, statistical result)
    """
    sv.set_start(start)
    sv.set_end(end)
    log_filtered = filtering.filter_traces(sv.indexed_log)
    log_trimmed = filtering.trim_log(log_filtered)

    result = dict()

    for trace in log_trimmed:
        result[trace.attributes["concept:name"]] = bipartite_matching_measuring(trace)

    return result


def bipartite_matching_measuring(trace):
    """
    Measure the duration of a trace

    Parameters
    ------------
    trace
        Trace
    Returns
    ------------
    (edges selected, statistical result)
        The edge selected and the corresponding aggregated statistics
    """

    graph = encode_trace_to_graph(trace)

    # if graph is not None:
    try:
        measures = []
        edges = solve_lp(graph)

        for edge in edges:
            measures.append(graph[edge[0]][edge[1]]["duration"])

        return (edges, helper.compute_time_statistics(measures))

    except Exception:
        pass


def encode_trace_to_graph(trace):
    """
    Encode a trace to a graph by converting every event of interest to a node

    Parameters
    ------------
    trace
        Trace
    Returns
    ------------
    graph
        Bipartite graph
    """
    graph = nx.DiGraph(cid=trace.attributes["concept:name"])

    "Create a node per event"
    for event in trace:
        graph.add_node(event["eid"], time=event["time:timestamp"], attri=event[sv.classifier])

    nodes_start = [node for node, attr_dict in graph.nodes(data=True) if attr_dict['attri'] in sv.start]
    nodes_end = [node for node, attr_dict in graph.nodes(data=True) if attr_dict['attri'] in sv.end]

    "Add edges"
    for node_start in nodes_start:
        for node_end in nodes_end:
            if graph.nodes[node_start]["time"] <= graph.nodes[node_end]["time"]:
                graph.add_edge(node_start, node_end, weight=helper.compute_weight(node_start, node_end),
                               duration=graph.nodes[node_end]["time"] - graph.nodes[node_start]["time"])

    "Filter out isolated nodes"
    nodes_to_removed = []
    for node in graph.nodes:
        if len(graph.in_edges(node)) == 0 and len(graph.out_edges(node)) == 0:
            nodes_to_removed.append(node)

    for node in nodes_to_removed:
        graph.remove_node(node)

    "Select the graph if there exists at least one edge"
    if len(graph.edges) != 0:
        return graph


def solve_lp(graph):
    """
    Solve the LP problem on a graph

    Parameters
    ------------
    graph
        NetworkX graph
    Returns
    ------------
    edges_selected
        List of selected edges in tuples of numbers
    """

    "Instantiate a Glop LP solver"
    solver = pywraplp.Solver('LinearSolver', pywraplp.Solver.GLOP_LINEAR_PROGRAMMING)

    "Set variables"
    variables = []

    for edge in graph.edges(data=True):
        variables.append(solver.NumVar(0.0, 1, str((edge[0], edge[1]))))

    "Set objective"
    objective = solver.Objective()

    for i in range(0, len(variables)):
        start_node = helper.get_edge(variables[i])[0]
        end_node = helper.get_edge(variables[i])[1]
        objective.SetCoefficient(variables[i], graph[start_node][end_node]["weight"])

    objective.SetMaximization()

    "Set constraints"
    constraints = [0] * len(graph.nodes())

    constraint_count = 0

    for node in graph.nodes():

        edges_of_node = list(graph.edges(node) if len(graph.edges(node)) > 0 else graph.in_edges(node))

        # The sum of edges of a node should not exceed 1, i.e., only one edge per node can be selected
        constraints[constraint_count] = solver.Constraint(0, 1)

        for variable in variables:
            if (helper.get_edge(variable)[0], helper.get_edge(variable)[1]) in edges_of_node:
                constraints[constraint_count].SetCoefficient(variable, 1)
            else:
                constraints[constraint_count].SetCoefficient(variable, 0)

        constraint_count += 1

    "Solve the LP"
    status = solver.Solve()

    edges_selected = []

    if status == solver.OPTIMAL:

        for variable in variables:

            if variable.solution_value() > 0:

                edges_selected.append((helper.get_edge(variable)[0], helper.get_edge(variable)[1]))

                if variable.solution_value() != 1.0 and variable.solution_value() != 0.0:
                    print("LP does not produce integer solution!")
                    break

    else:
        print("Some cases do not have performance info.")

    return edges_selected
