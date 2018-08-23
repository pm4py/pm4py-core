from graphviz import Digraph

def visualize(ts):
    viz = Digraph(ts.name, filename=ts.name+'.gv', engine='dot')

    # states
    viz.attr('node')
    for s in ts.states:
        viz.node(str(s.name))

    # arcs
    for t in ts.transitions:
        viz.edge(str(t.from_state.name), str(t.to_state.name))

    viz.attr(overlap='false')
    viz.attr(fontsize='11')

    return viz