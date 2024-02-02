'''
    This file is part of PM4Py (More Info: https://pm4py.fit.fraunhofer.de).

    PM4Py is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    PM4Py is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with PM4Py.  If not, see <https://www.gnu.org/licenses/>.
'''
from pm4py.util import nx_utils


def create_network_graph(net):
    """
    Transform a given Petri Net in a network graph. Each place and transition is node and gets duplicated.
    The even numbers handle the inputs of a node, the odds the output.
    :param net: PM4Py Petri Net representation
    :return: networkx.DiGraph(), bookkeeping dictionary
    """
    graph = nx_utils.DiGraph()
    places = sorted(list(net.places), key=lambda x: x.name)
    transitions = sorted(list(net.transitions), key=lambda x: x.name)
    nodes=set(places) | set(transitions)
    bookkeeping={}
    for index,el in enumerate(nodes):
        bookkeeping[el]=index*2
    for node in nodes:
        graph.add_node(bookkeeping[node])
        graph.add_node(bookkeeping[node]+1)
        graph.add_edge(bookkeeping[node], bookkeeping[node]+1, capacity=1)
    #add edges for outgoing arcs in former Petri Net
    for element in nodes:
        for arc in element.out_arcs:
            graph.add_edge(bookkeeping[element]+1, bookkeeping[arc.target], capacity=1)
    #add edges for ingoing arcs in former Petri Net
    for element in nodes:
        for arc in element.in_arcs:
            graph.add_edge(bookkeeping[arc.source]+1, bookkeeping[element], capacity=1)
    return graph,bookkeeping

def apply(net):
    """
    Using the max-flow min-cut theorem, we compute a list of nett well handled TP and PT pairs
    (T=transition, P=place)
    :param net: Petri Net
    :return: List
    """
    graph,booking=create_network_graph(net)
    pairs=[]
    for place in net.places:
        for transition in net.transitions:
            p=booking[place]
            t=booking[transition]
            if nx_utils.maximum_flow_value(graph, p+1, t)>1:
                pairs.append((p+1,t))
            if nx_utils.maximum_flow_value(graph, t+1, p)>1:
                pairs.append((t+1,p))
    return pairs
