import tempfile

from graphviz import Digraph

from copy import copy


def visualize(ts, parameters=None):
    if parameters is None:
        parameters = {}

    image_format = parameters["format"] if "format" in parameters else "png"
    show_labels = parameters["show_labels"] if "show_labels" in parameters else True
    show_names = parameters["show_names"] if "show_names" in parameters else True
    force_names = parameters["force_names"] if "force_names" in parameters else None

    if force_names:
        nts = copy(ts)
        for index, state in enumerate(nts.states):
            state.name = state.name + " (%.2f)" % (force_names[state])
        ts = nts

    filename = tempfile.NamedTemporaryFile(suffix='.gv')
    viz = Digraph(ts.name, filename=filename.name, engine='dot')

    # states
    viz.attr('node')
    for s in ts.states:
        if show_names:
            viz.node(str(s.name))
        else:
            viz.node(str(s.name), "")
    # arcs
    for t in ts.transitions:
        if show_labels:
            viz.edge(str(t.from_state.name), str(t.to_state.name), label=t.name)
        else:
            viz.edge(str(t.from_state.name), str(t.to_state.name))

    viz.attr(overlap='false')
    viz.attr(fontsize='11')

    viz.format = image_format

    return viz
