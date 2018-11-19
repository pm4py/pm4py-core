import tempfile

from graphviz import Digraph


def visualize(ts, parameters=None):
    if parameters is None:
        parameters = {}

    image_format = parameters["format"] if "format" in parameters else "png"

    filename = tempfile.NamedTemporaryFile(suffix='.gv')
    viz = Digraph(ts.name, filename=filename.name, engine='dot')

    # states
    viz.attr('node')
    for s in ts.states:
        viz.node(str(s.name))

    # arcs
    for t in ts.transitions:
        viz.edge(str(t.from_state.name), str(t.to_state.name))

    viz.attr(overlap='false')
    viz.attr(fontsize='11')

    viz.format = image_format

    return viz
