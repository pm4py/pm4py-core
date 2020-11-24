from pm4py.objects.bpmn.bpmn_graph import BPMN


class Counts:
    def __init__(self):
        self.number_processes = 0


def parse_element(bpmn_graph, counts, curr_el, parents, incoming_dict, outgoing_dict, nodes_dict, nodes_bounds,
                  flow_info, process=None, node=None, bpmn_element=None, flow=None, rec_depth=0):
    """
    Parses a BPMN element from the XML file
    """
    tag = curr_el.tag.lower()
    if tag.endswith("process"):
        process = curr_el.get("id")
    elif tag.endswith("shape"):
        bpmn_element = curr_el.get("bpmnElement")
    elif tag.endswith("task"):
        id = curr_el.get("id")
        name = curr_el.get("name").replace("\r", "").replace("\n", "")
        this_type = str(curr_el.tag)
        this_type = this_type[this_type.index("}") + 1:]
        task = BPMN.Task(name=name, type=this_type)
        bpmn_graph.add_node(task)
        node = task
        nodes_dict[id] = node
    elif tag.endswith("startevent"):
        id = curr_el.get("id")
        name = curr_el.get("name").replace("\r", " ").replace("\n", " ")
        start_event = BPMN.StartEvent(name=name)
        bpmn_graph.add_node(start_event)
        node = start_event
        nodes_dict[id] = node
    elif tag.endswith("endevent"):
        id = curr_el.get("id")
        name = curr_el.get("name").replace("\r", " ").replace("\n", " ")
        end_event = BPMN.EndEvent(name=name)
        bpmn_graph.add_node(end_event)
        node = end_event
        nodes_dict[id] = node
    elif tag.endswith("event"):
        id = curr_el.get("id")
        name = curr_el.get("name").replace("\r", " ").replace("\n", " ")
        this_type = str(curr_el.tag)
        this_type = this_type[this_type.index("}") + 1:]
        other_event = BPMN.OtherEvent(name=name, type=this_type)
        bpmn_graph.add_node(other_event)
        node = other_event
        nodes_dict[id] = node
    elif tag.endswith("edge"):
        bpmnElement = curr_el.get("bpmnElement")
        flow = bpmnElement
    elif tag.endswith("exclusivegateway"):
        id = curr_el.get("id")
        name = curr_el.get("name").replace("\r", "").replace("\n", "")
        exclusive_gateway = BPMN.ExclusiveGateway(name=name)
        bpmn_graph.add_node(exclusive_gateway)
        node = exclusive_gateway
        nodes_dict[id] = node
    elif tag.endswith("parallelgateway"):
        id = curr_el.get("id")
        name = curr_el.get("name").replace("\r", "").replace("\n", "")
        parallel_gateway = BPMN.ParallelGateway(name=name)
        bpmn_graph.add_node(parallel_gateway)
        node = parallel_gateway
        nodes_dict[id] = node
    elif tag.endswith("inclusivegateway"):
        id = curr_el.get("id")
        name = curr_el.get("name").replace("\r", "").replace("\n", "")
        inclusive_gateway = BPMN.InclusiveGateway(name=name)
        bpmn_graph.add_node(inclusive_gateway)
        node = inclusive_gateway
        nodes_dict[id] = node
    elif tag.endswith("incoming"):
        if node is not None:
            incoming_dict[curr_el.text] = node
    elif tag.endswith("outgoing"):
        if node is not None:
            outgoing_dict[curr_el.text] = node
    elif tag.endswith("waypoint"):
        if flow is not None:
            x = float(curr_el.get("x"))
            y = float(curr_el.get("y"))
            if not flow in flow_info:
                flow_info[flow] = []
            flow_info[flow].append((x, y))
    elif tag.endswith("label"):
        bpmn_element = None
    elif tag.endswith("bounds"):
        if bpmn_element is not None:
            x = float(curr_el.get("x"))
            y = float(curr_el.get("y"))
            width = float(curr_el.get("width"))
            height = float(curr_el.get("height"))
            nodes_bounds[bpmn_element] = {"x": x, "y": y, "width": width, "height": height}
    for child in curr_el:
        bpmn_graph = parse_element(bpmn_graph, counts, child, list(parents) + [child], incoming_dict, outgoing_dict,
                                   nodes_dict, nodes_bounds, flow_info, process=process, node=node,
                                   bpmn_element=bpmn_element,
                                   flow=flow, rec_depth=rec_depth + 1)
    if rec_depth == 0:
        for flow_id in flow_info:
            if flow_id in outgoing_dict and flow_id in incoming_dict:
                flow = BPMN.Flow(outgoing_dict[flow_id], incoming_dict[flow_id])
                bpmn_graph.add_flow(flow)
                flow.del_waypoints()
                for waypoint in flow_info[flow_id]:
                    flow.add_waypoint(waypoint)
        for node_id in nodes_bounds:
            if node_id in nodes_dict:
                bounds = nodes_bounds[node_id]
                node = nodes_dict[node_id]
                node.set_x(bounds["x"])
                node.set_y(bounds["y"])
                node.set_width(bounds["width"])
                node.set_height(bounds["height"])
    return bpmn_graph


def apply(path, parameters=None):
    """
    Imports a BPMN diagram from a file

    Parameters
    -------------
    path
        Path to the file
    parameters
        Parameters of the algorithm

    Returns
    -------------
    bpmn_graph
        BPMN graph
    """
    if parameters is None:
        parameters = {}

    from lxml import etree, objectify

    parser = etree.XMLParser(remove_comments=True)
    xml_tree = objectify.parse(path, parser=parser)
    root = xml_tree.getroot()
    bpmn_graph = BPMN()
    counts = Counts()
    incoming_dict = {}
    outgoing_dict = {}
    nodes_dict = {}
    nodes_bounds = {}
    flow_info = {}

    return parse_element(bpmn_graph, counts, root, [], incoming_dict, outgoing_dict, nodes_dict, nodes_bounds,
                         flow_info)
