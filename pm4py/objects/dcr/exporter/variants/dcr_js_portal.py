from lxml import etree
from pm4py.objects.dcr.obj import Relations, dcr_template
from copy import deepcopy


def export_dcr_xml(dcr, output_file_name, dcr_title):
    '''
    Writes a DCR graph object to disk in the ``.xml`` file format (exported as ``.xml`` file).
    The file is to be visualised using the following link: https://hugoalopez-dtu.github.io/dcr-js/

    Parameters
    -----------
    dcr
        the DCR graph
    output_file_name
        dcrxml file name
    dcr_title
        title of the DCR graph
    '''

    dcr = clean_output(dcr)
    event_labels = list(dcr['labelMapping'].keys())
    event_ids = []
    for event in list(dcr['labelMapping'].values()):
        for event_id in event:
            event_ids.append(event_id)

    root = etree.Element("dcrgraph")
    if dcr_title:
        root.set("title", dcr_title)
    specification = etree.SubElement(root, "specification")
    resources = etree.SubElement(specification, "resources")
    events = etree.SubElement(resources, "events")
    subprocesses = etree.SubElement(resources, "subProcesses")
    labels = etree.SubElement(resources, "labels")
    labelMappings = etree.SubElement(resources, "labelMappings")

    constraints = etree.SubElement(specification, "constraints")
    conditions = etree.SubElement(constraints, "conditions")
    responses = etree.SubElement(constraints, "responses")
    excludes = etree.SubElement(constraints, "excludes")
    includes = etree.SubElement(constraints, "includes")

    runtime = etree.SubElement(root, "runtime")
    marking = etree.SubElement(runtime, "marking")
    executed = etree.SubElement(marking, "executed")
    included = etree.SubElement(marking, "included")
    pendingResponse = etree.SubElement(marking, "pendingResponses")

    # Each event's coordinates for visualisation
    xcoord = {}
    ycoord = {}
    x = 0
    y = 0
    for event in dcr['events']:
        xcoord[event] = x
        ycoord[event] = y
        x += 300

        if x > 1200:
            x = 0
            y += 300

    for event in dcr['events']:
        xml_event = etree.SubElement(events, "event")
        xml_event.set("id", event)
        xml_event_custom = etree.SubElement(xml_event, "custom")
        xml_visual = etree.SubElement(xml_event_custom, "visualization")
        xml_location = etree.SubElement(xml_visual, "location")
        xml_location.set("xLoc", str(xcoord[event]))
        xml_location.set("yLoc", str(ycoord[event]))
        xml_size = etree.SubElement(xml_visual, "size")
        xml_size.set("width", "130")
        xml_size.set("height", "150")
        xml_label = etree.SubElement(labels, "label")
        xml_label.set("id", event)
        xml_labelMapping = etree.SubElement(labelMappings, "labelMapping")
        xml_labelMapping.set("eventId", event)
        label_id = event_labels[event_ids.index(event)]
        xml_labelMapping.set("labelId", label_id)

        for event_prime in dcr['events']:
            if event_prime in dcr["conditionsFor"] and event in dcr["conditionsFor"][event_prime]:
                xml_condition = etree.SubElement(conditions, "condition")
                xml_condition.set("sourceId", event)
                xml_condition.set("targetId", event_prime)
                xml_condition_custom = etree.SubElement(xml_condition, "custom")
                xml_waypoints = etree.SubElement(xml_condition_custom, "waypoints")
                create_arrows(xml_waypoints, xcoord,ycoord, event, event_prime)
                xml_custom_id = etree.SubElement(xml_condition_custom, "id")
                xml_custom_id.set("id", "Relation_" + event + "_" + event_prime + "_condition")
            if event in dcr["responseTo"] and event_prime in dcr["responseTo"][event]:
                xml_response = etree.SubElement(responses, "response")
                xml_response.set("sourceId", event)
                xml_response.set("targetId", event_prime)
                xml_response_custom = etree.SubElement(xml_response, "custom")
                xml_waypoints = etree.SubElement(xml_response_custom, "waypoints")
                create_arrows(xml_waypoints, xcoord, ycoord, event, event_prime)
                xml_custom_id = etree.SubElement(xml_response_custom, "id")
                xml_custom_id.set("id", "Relation_" + event + "_" + event_prime + "_response")
            if event in dcr["includesTo"] and event_prime in dcr["includesTo"][event]:
                xml_include = etree.SubElement(includes, "include")
                xml_include.set("sourceId", event)
                xml_include.set("targetId", event_prime)
                xml_include_custom = etree.SubElement(xml_include, "custom")
                xml_waypoints = etree.SubElement(xml_include_custom, "waypoints")
                create_arrows(xml_waypoints, xcoord, ycoord, event, event_prime)
                xml_custom_id = etree.SubElement(xml_include_custom, "id")
                xml_custom_id.set("id", "Relation_" + event + "_" + event_prime + "_include")
            if event in dcr["excludesTo"] and event_prime in dcr["excludesTo"][event]:
                xml_exclude = etree.SubElement(excludes, "exclude")
                xml_exclude.set("sourceId", event)
                xml_exclude.set("targetId", event_prime)
                xml_exclude_custom = etree.SubElement(xml_exclude, "custom")
                xml_waypoints = etree.SubElement(xml_exclude_custom, "waypoints")

                # Creates a self-exclude arrow to avoid having just the arrowhead sitting at the centre of the event
                if event == event_prime:
                    xml_waypoint = etree.SubElement(xml_waypoints, "waypoint")
                    xml_waypoint.set("x", str(xcoord[event]+65))
                    xml_waypoint.set("y", str(ycoord[event]+150))
                    xml_waypoint = etree.SubElement(xml_waypoints, "waypoint")
                    xml_waypoint.set("x", str(xcoord[event]+65))
                    xml_waypoint.set("y", str(ycoord[event]+175))
                    xml_waypoint = etree.SubElement(xml_waypoints, "waypoint")
                    xml_waypoint.set("x", str(xcoord[event]-25))
                    xml_waypoint.set("y", str(ycoord[event]+175))
                    xml_waypoint = etree.SubElement(xml_waypoints, "waypoint")
                    xml_waypoint.set("x", str(xcoord[event]-25))
                    xml_waypoint.set("y", str(ycoord[event]+75))
                    xml_waypoint = etree.SubElement(xml_waypoints, "waypoint")
                    xml_waypoint.set("x", str(xcoord[event]))
                    xml_waypoint.set("y", str(ycoord[event]+75))
                else:
                    create_arrows(xml_waypoints, xcoord, ycoord, event, event_prime)
                xml_custom_id = etree.SubElement(xml_exclude_custom, "id")
                xml_custom_id.set("id", "Relation_" + event + "_" + event_prime + "_exclude")

        if event in dcr['marking']['executed']:
            marking_exec = etree.SubElement(executed, "event")
            marking_exec.set("id", event)
        if event in dcr['marking']['included']:
            marking_incl = etree.SubElement(included, "event")
            marking_incl.set("id", event)
        if event in dcr['marking']['pending']:
            marking_pend = etree.SubElement(pendingResponse, "event")
            marking_pend.set("id", event)

    tree = etree.ElementTree(root)
    tree.write(output_file_name, pretty_print=True, xml_declaration=True, encoding="utf-8", standalone="yes")


def create_arrows(xml_waypoints, xcoord, ycoord, event, event_prime):
    # Helper function that connects two events with corresponding constraint arrow
    if xcoord[event] < xcoord[event_prime] and ycoord[event] < ycoord[event_prime]:
        xoffset = 130
        xprimeoffset = 0
        yoffset = 75
        yprimeoffset = 75
    elif xcoord[event] < xcoord[event_prime] and ycoord[event] > ycoord[event_prime]:
        xoffset = 130
        xprimeoffset = 0
        yoffset = 75
        yprimeoffset = 75
    elif xcoord[event] > xcoord[event_prime] and ycoord[event] < ycoord[event_prime]:
        xoffset = 0
        xprimeoffset = 130
        yoffset = 75
        yprimeoffset = 75
    elif xcoord[event] > xcoord[event_prime] and ycoord[event] > ycoord[event_prime]:
        xoffset = 0
        xprimeoffset = 130
        yoffset = 75
        yprimeoffset = 75
    elif xcoord[event] == xcoord[event_prime] and ycoord[event] < ycoord[event_prime]:
        xoffset = 65
        xprimeoffset = 65
        yoffset = 150
        yprimeoffset = 0
    elif xcoord[event] == xcoord[event_prime] and ycoord[event] > ycoord[event_prime]:
        xoffset = 65
        xprimeoffset = 65
        yoffset = 0
        yprimeoffset = 150
    elif xcoord[event] < xcoord[event_prime] and ycoord[event] == ycoord[event_prime]:
        xoffset = 130
        xprimeoffset = 0
        yoffset = 75
        yprimeoffset = 75
    elif xcoord[event] > xcoord[event_prime] and ycoord[event] == ycoord[event_prime]:
        xoffset = 0
        xprimeoffset = 130
        yoffset = 75
        yprimeoffset = 75

    xml_waypoint = etree.SubElement(xml_waypoints, "waypoint")
    xml_waypoint.set("x", str(xcoord[event]+xoffset))
    xml_waypoint.set("y", str(ycoord[event]+yoffset))
    xml_waypoint = etree.SubElement(xml_waypoints, "waypoint")
    xml_waypoint.set("x", str((xcoord[event]+xoffset+xcoord[event_prime]+xprimeoffset)/2))
    xml_waypoint.set("y", str(ycoord[event]+yoffset))
    xml_waypoint = etree.SubElement(xml_waypoints, "waypoint")
    xml_waypoint.set("x", str((xcoord[event]+xoffset+xcoord[event_prime]+xprimeoffset)/2))
    xml_waypoint.set("y", str(ycoord[event_prime]+yprimeoffset))
    xml_waypoint = etree.SubElement(xml_waypoints, "waypoint")
    xml_waypoint.set("x", str(xcoord[event_prime]+xprimeoffset))
    xml_waypoint.set("y", str(ycoord[event_prime]+yprimeoffset))


def clean_output(dcr):
    # Helper function that removes spaces to satisfy the dcr-js portal
    graph = deepcopy(dcr_template)
    for k, v in dcr.__dict__.items():
        item = list(k.split('_'))
        K = item[len(item)-1]
        if K in (relation.value for relation in Relations):
            v_new = {}
            for k2, v2 in v.items():
                v_new[k2.strip().replace(' ', '_')] = set([v3.strip().replace(' ', '_') for v3 in v2])
            graph[K] = v_new
        elif K in ['conditionsForDelays', 'responseToDeadlines']:
            v_new = {}
            for k2, v2 in v.items():
                v_new[k2.strip().replace(' ', '_')] = set([(v3.strip().replace(' ', '_'), d) for (v3, d) in v2])
            graph[K] = v_new
        elif K == 'marking':
            for k2 in ['executed', 'included', 'pending']:
                new_v = set([v2.strip().replace(' ', '_') for v2 in dcr.__dict__[k][k2]])
                graph[K][k2] = new_v
        elif K in ['subprocesses', 'nestings', 'labelMapping', 'roleAssignments', 'readRoleAssignments']:
            v_new = {}
            for k2, v2 in v.items():
                v_new[k2.strip().replace(' ', '_')] = set([v3.strip().replace(' ', '_') for v3 in v2])
            graph[K] = v_new
        else:
            new_v = set([v2.strip().replace(' ', '_') for v2 in dcr.__dict__[k]])
            graph[K] = set(new_v)
    return graph
