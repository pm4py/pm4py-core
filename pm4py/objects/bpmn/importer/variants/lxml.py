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
from pm4py.objects.bpmn.obj import BPMN
from pm4py.util import constants
import uuid


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
        name = curr_el.get("name").replace("\r", " ").replace("\n", " ") if "name" in curr_el else str(uuid.uuid4())
        start_event = BPMN.StartEvent(name=name)
        bpmn_graph.add_node(start_event)
        node = start_event
        nodes_dict[id] = node
    elif tag.endswith("endevent"):
        id = curr_el.get("id")
        name = curr_el.get("name").replace("\r", " ").replace("\n", " ") if "name" in curr_el else str(uuid.uuid4())
        end_event = BPMN.EndEvent(name=name)
        bpmn_graph.add_node(end_event)
        node = end_event
        nodes_dict[id] = node
    elif tag.endswith("event"):
        id = curr_el.get("id")
        name = curr_el.get("name").replace("\r", " ").replace("\n", " ") if "name" in curr_el else str(uuid.uuid4())
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
        name = curr_el.get("name").replace("\r", "").replace("\n", "") if "name" in curr_el else str(uuid.uuid4())
        exclusive_gateway = BPMN.ExclusiveGateway(name=name)
        bpmn_graph.add_node(exclusive_gateway)
        node = exclusive_gateway
        nodes_dict[id] = node
    elif tag.endswith("parallelgateway"):
        id = curr_el.get("id")
        name = curr_el.get("name").replace("\r", "").replace("\n", "") if "name" in curr_el else str(uuid.uuid4())
        parallel_gateway = BPMN.ParallelGateway(name=name)
        bpmn_graph.add_node(parallel_gateway)
        node = parallel_gateway
        nodes_dict[id] = node
    elif tag.endswith("inclusivegateway"):
        id = curr_el.get("id")
        name = curr_el.get("name").replace("\r", "").replace("\n", "") if "name" in curr_el else str(uuid.uuid4())
        inclusive_gateway = BPMN.InclusiveGateway(name=name)
        bpmn_graph.add_node(inclusive_gateway)
        node = inclusive_gateway
        nodes_dict[id] = node
    elif tag.endswith("incoming"):
        if node is not None:
            incoming_dict[curr_el.text.strip()] = node
    elif tag.endswith("outgoing"):
        if node is not None:
            outgoing_dict[curr_el.text.strip()] = node
    elif tag.endswith("sequenceflow"):
        seq_flow_id = curr_el.get("id")
        source_ref = curr_el.get("sourceRef")
        target_ref = curr_el.get("targetRef")
        # fix 28/04/2021: do not assume anymore to read the nodes before the edges
        incoming_dict[seq_flow_id] = target_ref
        outgoing_dict[seq_flow_id] = source_ref
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
        for seq_flow_id in incoming_dict:
            if incoming_dict[seq_flow_id] in nodes_dict:
                incoming_dict[seq_flow_id] = nodes_dict[incoming_dict[seq_flow_id]]
        for seq_flow_id in outgoing_dict:
            if outgoing_dict[seq_flow_id] in nodes_dict:
                outgoing_dict[seq_flow_id] = nodes_dict[outgoing_dict[seq_flow_id]]
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


def import_xml_tree_from_root(root):
    """
    Imports a BPMN graph from (the root of) an XML tree

    Parameters
    -------------
    root
        Root of the tree

    Returns
    -------------
    bpmn_graph
        BPMN graph
    """
    bpmn_graph = BPMN()
    counts = Counts()
    incoming_dict = {}
    outgoing_dict = {}
    nodes_dict = {}
    nodes_bounds = {}
    flow_info = {}

    return parse_element(bpmn_graph, counts, root, [], incoming_dict, outgoing_dict, nodes_dict, nodes_bounds,
                         flow_info)


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

    return import_xml_tree_from_root(xml_tree.getroot())


def import_from_string(bpmn_string, parameters=None):
    """
    Imports a BPMN diagram from a string

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

    if type(bpmn_string) is str:
        bpmn_string = bpmn_string.encode(constants.DEFAULT_ENCODING)

    from lxml import etree, objectify

    parser = etree.XMLParser(remove_comments=True)
    root = objectify.fromstring(bpmn_string, parser=parser)

    return import_xml_tree_from_root(root)
