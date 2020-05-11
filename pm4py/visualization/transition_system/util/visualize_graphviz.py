import tempfile
from copy import copy

from graphviz import Digraph
from pm4py.util import exec_utils
from pm4py.visualization.transition_system.parameters import Parameters


def visualize(ts, parameters=None):
    if parameters is None:
        parameters = {}

    image_format = exec_utils.get_param_value(Parameters.FORMAT, parameters, "png")
    show_labels = exec_utils.get_param_value(Parameters.SHOW_LABELS, parameters, True)
    show_names = exec_utils.get_param_value(Parameters.SHOW_NAMES, parameters, True)
    force_names = exec_utils.get_param_value(Parameters.FORCE_NAMES, parameters, None)
    fillcolors = exec_utils.get_param_value(Parameters.FILLCOLORS, parameters, {})

    for state in ts.states:
        state.label = state.name

    perc_char = '%'

    if force_names:
        nts = copy(ts)
        for index, state in enumerate(nts.states):
            state.name = state.name + " (%.2f)" % (force_names[state])
            state.label = "%.2f" % (force_names[state] * 100.0)
            state.label = state.label + perc_char
        ts = nts

    filename = tempfile.NamedTemporaryFile(suffix='.gv')
    viz = Digraph(ts.name, filename=filename.name, engine='dot', graph_attr={'bgcolor': 'transparent'})

    # states
    viz.attr('node')
    for s in ts.states:
        if show_names:
            if s in fillcolors:
                viz.node(str(id(s)), str(s.label), style="filled", fillcolor=fillcolors[s])
            else:
                viz.node(str(id(s)), str(s.label))
        else:
            if s in fillcolors:
                viz.node(str(id(s)), "", style="filled", fillcolor=fillcolors[s])
            else:
                viz.node(str(id(s)), "")
    # arcs
    for t in ts.transitions:
        if show_labels:
            viz.edge(str(id(t.from_state)), str(id(t.to_state)), label=t.name)
        else:
            viz.edge(str(id(t.from_state)), str(id(t.to_state)))

    viz.attr(overlap='false')
    viz.attr(fontsize='11')

    viz.format = image_format

    return viz
