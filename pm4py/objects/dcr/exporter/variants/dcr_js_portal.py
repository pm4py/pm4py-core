from lxml import etree


def export_dcr_xml(dcr, output_file_name, dcr_title):
    '''
    dcr : the mined graph
    output_file_name: dcrxml file name without extension
    '''
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
        xml_labelMapping.set("labelId", event)

        for event_prime in dcr['events']:
            if event in dcr["conditionsFor"] and event_prime in dcr["conditionsFor"][event]:
                xml_condition = etree.SubElement(conditions, "condition")
                xml_condition.set("sourceId", event)
                xml_condition.set("targetId", event_prime)
                xml_condition_custom = etree.SubElement(xml_condition, "custom")
                xml_waypoints = etree.SubElement(xml_condition_custom, "waypoints")
                xml_waypoint = etree.SubElement(xml_waypoints, "waypoint")
                xml_waypoint.set("x", str(xcoord[event]+65))
                xml_waypoint.set("y", str(ycoord[event]+75))
                xml_waypoint = etree.SubElement(xml_waypoints, "waypoint")
                xml_waypoint.set("x", str(xcoord[event_prime]+65))
                xml_waypoint.set("y", str(ycoord[event_prime]+75))
                xml_custom_id = etree.SubElement(xml_condition_custom, "id")
                xml_custom_id.set("id", "Relation_" + event + "_" + event_prime + "_condition")
            if event in dcr["responseTo"] and event_prime in dcr["responseTo"][event]:
                xml_response = etree.SubElement(responses, "response")
                xml_response.set("sourceId", event)
                xml_response.set("targetId", event_prime)
                xml_response_custom = etree.SubElement(xml_response, "custom")
                xml_waypoints = etree.SubElement(xml_response_custom, "waypoints")
                xml_waypoint = etree.SubElement(xml_waypoints, "waypoint")
                xml_waypoint.set("x", str(xcoord[event]+65))
                xml_waypoint.set("y", str(ycoord[event]+75))
                xml_waypoint = etree.SubElement(xml_waypoints, "waypoint")
                xml_waypoint.set("x", str(xcoord[event_prime]+65))
                xml_waypoint.set("y", str(ycoord[event_prime]+75))
                xml_custom_id = etree.SubElement(xml_response_custom, "id")
                xml_custom_id.set("id", "Relation_" + event + "_" + event_prime + "_response")
            if event in dcr["includesTo"] and event_prime in dcr["includesTo"][event]:
                xml_include = etree.SubElement(includes, "include")
                xml_include.set("sourceId", event)
                xml_include.set("targetId", event_prime)
                xml_include_custom = etree.SubElement(xml_include, "custom")
                xml_waypoints = etree.SubElement(xml_include_custom, "waypoints")
                xml_waypoint = etree.SubElement(xml_waypoints, "waypoint")
                xml_waypoint.set("x", str(xcoord[event]+65))
                xml_waypoint.set("y", str(ycoord[event]+75))
                xml_waypoint = etree.SubElement(xml_waypoints, "waypoint")
                xml_waypoint.set("x", str(xcoord[event_prime]+65))
                xml_waypoint.set("y", str(ycoord[event_prime]+75))
                xml_custom_id = etree.SubElement(xml_include_custom, "id")
                xml_custom_id.set("id", "Relation_" + event + "_" + event_prime + "_include")
            if event in dcr["excludesTo"] and event_prime in dcr["excludesTo"][event]:
                xml_exclude = etree.SubElement(excludes, "exclude")
                xml_exclude.set("sourceId", event)
                xml_exclude.set("targetId", event_prime)
                xml_exclude_custom = etree.SubElement(xml_exclude, "custom")
                xml_waypoints = etree.SubElement(xml_exclude_custom, "waypoints")
                xml_waypoint = etree.SubElement(xml_waypoints, "waypoint")
                xml_waypoint.set("x", str(xcoord[event]+65))
                xml_waypoint.set("y", str(ycoord[event]+75))
                xml_waypoint = etree.SubElement(xml_waypoints, "waypoint")
                xml_waypoint.set("x", str(xcoord[event_prime]+65))
                xml_waypoint.set("y", str(ycoord[event_prime]+75))
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
