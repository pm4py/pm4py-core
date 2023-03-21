from lxml import etree


def export_dcr_graph(dcr, root, parent=None):
    for event in dcr['events']:
        xml_event = etree.SubElement(root, "events")
        xml_event_id = etree.SubElement(xml_event, "id")
        xml_event_id.text = event
        xml_event_label = etree.SubElement(xml_event, "label")
        xml_event_label.text = event
        if parent:
            xml_event_parent = etree.SubElement(xml_event, "parent")
            xml_event_parent.text = parent

        for event_prime in dcr['events']:
            if event in dcr["conditionsFor"] and event_prime in dcr["conditionsFor"][event]:
                xml_condition = etree.SubElement(root, "rules")
                xml_type = etree.SubElement(xml_condition, "type")
                xml_type.text = "condition"
                xml_source = etree.SubElement(xml_condition, "source")
                xml_source.text = event_prime
                xml_target = etree.SubElement(xml_condition, "target")
                xml_target.text = event
                xml_target = etree.SubElement(xml_condition, "duration")
                if 'conditionsForDelays' in dcr.keys():
                    time = dcr['conditionsForDelays'][event][event_prime]
                    #TODO: to iso format automatically
                    xml_target.text = f"P{time}D"
                else:
                    xml_target.text = "P0D"
            if event in dcr["responseTo"] and event_prime in dcr["responseTo"][event]:
                xml_response = etree.SubElement(root, "rules")
                xml_type = etree.SubElement(xml_response, "type")
                xml_type.text = "response"
                xml_source = etree.SubElement(xml_response, "source")
                xml_source.text = event
                xml_target = etree.SubElement(xml_response, "target")
                xml_target.text = event_prime
                xml_target = etree.SubElement(xml_response, "duration")
                if 'responseToDeadlines' in dcr.keys():
                    time = dcr['responseToDeadlines'][event][event_prime]
                    #TODO: to iso format automatically
                    xml_target.text = f"P{time}D"
                else:
                    xml_target.text = "P0D"
            if event in dcr["includesTo"] and event_prime in dcr["includesTo"][event]:
                xml_include = etree.SubElement(root, "rules")
                xml_type = etree.SubElement(xml_include, "type")
                xml_type.text = "include"
                xml_source = etree.SubElement(xml_include, "source")
                xml_source.text = event
                xml_target = etree.SubElement(xml_include, "target")
                xml_target.text = event_prime
            if event in dcr["excludesTo"] and event_prime in dcr["excludesTo"][event]:
                xml_exclude = etree.SubElement(root, "rules")
                xml_type = etree.SubElement(xml_exclude, "type")
                xml_type.text = "exclude"
                xml_source = etree.SubElement(xml_exclude, "source")
                xml_source.text = event
                xml_target = etree.SubElement(xml_exclude, "target")
                xml_target.text = event_prime

        # if event in dcr['marking']['executed']:
        #     marking_exec = etree.SubElement(executed, "event")
        #     marking_exec.set("id", event)
        # if event in dcr['marking']['included']:
        #     marking_incl = etree.SubElement(included, "event")
        #     marking_incl.set("id", event)
        # if event in dcr['marking']['pending']:
        #     marking_pend = etree.SubElement(pendingResponse,"event")
        #     marking_pend.set("id",event)


def export_dcr_xml(dcr, output_file_name, dcr_title, dcr_description=None):
    '''
    dcr : the mined graph
    output_file_name: dcrxml file name without extension
    '''
    root = etree.Element("DCRModel")
    if dcr_title:
        title = etree.SubElement(root, "title")
        title.text = dcr_title
    if dcr_description:
        desc = etree.SubElement(root, "description")
        desc.text = dcr_description
    graph_type = etree.SubElement(root, "graphType")
    graph_type.text = "DCRModel"
    # this needs to exist so it can be imported inside dcr graphs with the app
    role = etree.SubElement(root, "roles")
    role_title = etree.SubElement(role, "title")
    role_title.text = "User"
    role_description = etree.SubElement(role, "description")
    role_description.text = "Dummy user"


    export_dcr_graph(dcr, root)

    if 'subprocesses' in dcr:
        for sp_name, sp_dcr in dcr['subprocesses'].items():
            xml_event = etree.SubElement(root, "events")
            xml_event_id = etree.SubElement(xml_event, "id")
            xml_event_id.text = sp_name
            xml_event_label = etree.SubElement(xml_event, "label")
            xml_event_label.text = sp_name
            xml_event_type = etree.SubElement(xml_event, "type")
            xml_event_type.text = "subprocess"  # TODO: try "nesting" if subprocess doesn't work

            export_dcr_graph(sp_dcr, root, sp_name)

    tree = etree.ElementTree(root)
    tree.write(output_file_name, pretty_print=True)
