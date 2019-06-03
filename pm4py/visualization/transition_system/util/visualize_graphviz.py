import tempfile
from copy import copy

from graphviz import Digraph


def visualize(ts, parameters=None):
    if parameters is None:
        parameters = {}

    image_format = parameters["format"] if "format" in parameters else "png"
    show_labels = parameters["show_labels"] if "show_labels" in parameters else True
    show_names = parameters["show_names"] if "show_names" in parameters else True
    force_names = parameters["force_names"] if "force_names" in parameters else None
    fillcolors = parameters["fillcolors"] if "fillcolors" in parameters else {}

    for state in ts.states:
        state.label = state.name

    perc_char = '%'

    if force_names:
        nts = copy(ts)
        for index, state in enumerate(nts.states):
            state.name = state.name + " (%.2f)" % (force_names[state])
            state.label = "%.2f" % (force_names[state]*100.0)
            state.label = state.label + perc_char
        ts = nts

    filename = tempfile.NamedTemporaryFile(suffix='.gv')
    viz = Digraph(ts.name, filename=filename.name, engine='dot', graph_attr={'bgcolor':'transparent'})

    # states
    viz.attr('node')
    for s in ts.states:
        if show_names:
            if s in fillcolors:
                viz.node(str(hash(str(s.name))), str(s.label), style="filled", fillcolor=fillcolors[s])
            else:
                viz.node(str(hash(str(s.name))), str(s.label))
        else:
            if s in fillcolors:
                viz.node(str(hash(str(s.name))), "", style="filled", fillcolor=fillcolors[s])
            else:
                viz.node(str(hash(str(s.name))), "")
    # arcs
    for t in ts.transitions:
        if show_labels:
            viz.edge(str(hash(str(t.from_state.name))), str(hash(str(t.to_state.name))), label=t.name)
        else:
            viz.edge(str(hash(str(t.from_state.name))), str(hash(str(t.to_state.name))))

    viz.attr(overlap='false')
    viz.attr(fontsize='11')

    viz.format = image_format

    return viz
