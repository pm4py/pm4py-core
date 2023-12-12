from lxml import etree


def export_dcr_xml(dcr, output_file_name, dcr_title):
    '''
    Writes a DCR graph object to disk in the ``.xml`` file format (exported as ``.xml`` file).

    Parameters
    -----------
    dcr
        the DCR graph
    output_file_name
        dcrxml file name
    dcr_title
        title of the DCR graph
    '''
    root = etree.Element("dcrgraph")
    if dcr_title:
        root.set("title", dcr_title)
    specification = etree.SubElement(root, "specification")
    resources = etree.SubElement(specification, "resources")
    events = etree.SubElement(resources, "events")
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

    for event in dcr['events']:
        xml_event = etree.SubElement(events, "event")
        xml_event.set("id", event)
        xml_label = etree.SubElement(labels, "label")
        xml_label.set("id", event)
        xml_labelMapping = etree.SubElement(labelMappings, "labelMapping")
        xml_labelMapping.set("eventId", event)
        xml_labelMapping.set("labelId", event)

        for event_prime in dcr['events']:
            if event in dcr["conditionsFor"] and event_prime in dcr["conditionsFor"][event]:
                xml_condition = etree.SubElement(conditions, "condition")
                xml_condition.set("sourceId", event_prime)
                xml_condition.set("targetId", event)
            if event in dcr["responseTo"] and event_prime in dcr["responseTo"][event]:
                xml_response = etree.SubElement(responses, "response")
                xml_response.set("sourceId", event)
                xml_response.set("targetId", event_prime)
            if event in dcr["includesTo"] and event_prime in dcr["includesTo"][event]:
                xml_include = etree.SubElement(includes, "include")
                xml_include.set("sourceId", event)
                xml_include.set("targetId", event_prime)
            if event in dcr["excludesTo"] and event_prime in dcr["excludesTo"][event]:
                xml_exclude = etree.SubElement(excludes, "exclude")
                xml_exclude.set("sourceId", event)
                xml_exclude.set("targetId", event_prime)

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
    tree.write(output_file_name, pretty_print=True)
