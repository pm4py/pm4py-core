def apply(net, im, fm, parameters=None):
    """
    Converts an accepting Petri net into a BPMN diagram

    Parameters
    --------------
    accepting_petri_net
        Accepting Petri net (list containing net + im + fm)
    parameters
        Parameters of the algorithm

    Returns
    --------------
    bpmn_graph
        BPMN diagram
    """
    if parameters is None:
        parameters = {}

    from pm4py.objects.bpmn.bpmn_graph import BPMN
    from pm4py.objects.bpmn.util import reduction

    bpmn_graph = BPMN()

    entering_dictio = {}
    exiting_dictio = {}

    for place in net.places:
        node = BPMN.ExclusiveGateway()
        bpmn_graph.add_node(node)
        entering_dictio[place] = node
        exiting_dictio[place] = node

    for trans in net.transitions:
        if trans.label is None:
            if len(trans.in_arcs) > 1 or len(trans.out_arcs) > 1:
                node = BPMN.ParallelGateway()
            else:
                node = BPMN.ExclusiveGateway()
            bpmn_graph.add_node(node)
            entering_dictio[trans] = node
            exiting_dictio[trans] = node
        else:
            if len(trans.in_arcs) > 1:
                entering_node = BPMN.ParallelGateway()
            else:
                entering_node = BPMN.ExclusiveGateway()

            if len(trans.out_arcs) > 1:
                exiting_node = BPMN.ParallelGateway()
            else:
                exiting_node = BPMN.ExclusiveGateway()

            task = BPMN.Task(name=trans.label)
            bpmn_graph.add_node(task)

            bpmn_graph.add_flow(BPMN.Flow(entering_node, task))
            bpmn_graph.add_flow(BPMN.Flow(task, exiting_node))

            entering_dictio[trans] = entering_node
            exiting_dictio[trans] = exiting_node

    for arc in net.arcs:
        bpmn_graph.add_flow(BPMN.Flow(exiting_dictio[arc.source], entering_dictio[arc.target]))

    start_node = BPMN.StartEvent()
    end_node = BPMN.EndEvent()
    bpmn_graph.add_node(start_node)
    bpmn_graph.add_node(end_node)
    for place in im:
        bpmn_graph.add_flow(BPMN.Flow(start_node, entering_dictio[place]))
    for place in fm:
        bpmn_graph.add_flow(BPMN.Flow(exiting_dictio[place], end_node))

    bpmn_graph = reduction.apply(bpmn_graph)

    return bpmn_graph
