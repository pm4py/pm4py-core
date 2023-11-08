from lxml import etree


def export_dcr_graph(dcr, root, parents_dict=None, replace_whitespace=''):
    for event in dcr['events']:
        xml_event = etree.SubElement(root, "events")
        xml_event_id = etree.SubElement(xml_event, "id")
        xml_event_id.text = event.replace(' ', replace_whitespace)
        xml_event_label = etree.SubElement(xml_event, "label")
        xml_event_label.text = event.replace(' ', replace_whitespace)
        if parents_dict and event in parents_dict:
            xml_event_parent = etree.SubElement(xml_event, "parent")
            xml_event_parent.text = parents_dict[event].replace(' ', replace_whitespace)

        for event_prime in dcr['events']:
            if event in dcr["conditionsFor"] and event_prime in dcr["conditionsFor"][event]:
                xml_condition = etree.SubElement(root, "rules")
                xml_type = etree.SubElement(xml_condition, "type")
                xml_type.text = "condition"
                xml_source = etree.SubElement(xml_condition, "source")
                xml_source.text = event_prime.replace(' ', replace_whitespace)
                xml_target = etree.SubElement(xml_condition, "target")
                xml_target.text = event.replace(' ', replace_whitespace)
                if 'conditionsForDelays' in dcr.__dict__.keys() and event in dcr['conditionsForDelays'] \
                        and event_prime in dcr['conditionsForDelays'][event]:
                    time = dcr['conditionsForDelays'][event][event_prime]
                    if time.floor(freq='S').to_numpy() > 0:
                        xml_target = etree.SubElement(xml_condition, "duration")
                        xml_target.text = time.floor(freq='S').isoformat()
            if event in dcr["responseTo"] and event_prime in dcr["responseTo"][event]:
                xml_response = etree.SubElement(root, "rules")
                xml_type = etree.SubElement(xml_response, "type")
                xml_type.text = "response"
                xml_source = etree.SubElement(xml_response, "source")
                xml_source.text = event.replace(' ', replace_whitespace)
                xml_target = etree.SubElement(xml_response, "target")
                xml_target.text = event_prime.replace(' ', replace_whitespace)
                if 'responseToDeadlines' in dcr.__dict__.keys() and event in dcr['responseToDeadlines'] \
                        and event_prime in dcr['responseToDeadlines'][event]:
                    time = dcr['responseToDeadlines'][event][event_prime]
                    if time.floor(freq='S').to_numpy() > 0:
                        xml_target = etree.SubElement(xml_response, "duration")
                        xml_target.text = time.floor(freq='S').isoformat()
            if event in dcr["includesTo"] and event_prime in dcr["includesTo"][event]:
                xml_include = etree.SubElement(root, "rules")
                xml_type = etree.SubElement(xml_include, "type")
                xml_type.text = "include"
                xml_source = etree.SubElement(xml_include, "source")
                xml_source.text = event.replace(' ', replace_whitespace)
                xml_target = etree.SubElement(xml_include, "target")
                xml_target.text = event_prime.replace(' ', replace_whitespace)
            if event in dcr["excludesTo"] and event_prime in dcr["excludesTo"][event]:
                xml_exclude = etree.SubElement(root, "rules")
                xml_type = etree.SubElement(xml_exclude, "type")
                xml_type.text = "exclude"
                xml_source = etree.SubElement(xml_exclude, "source")
                xml_source.text = event.replace(' ', replace_whitespace)
                xml_target = etree.SubElement(xml_exclude, "target")
                xml_target.text = event_prime.replace(' ', replace_whitespace)
            if event in dcr["milestonesFor"] and event_prime in dcr["milestonesFor"][event]:
                xml_exclude = etree.SubElement(root, "rules")
                xml_type = etree.SubElement(xml_exclude, "type")
                xml_type.text = "milestone"
                xml_source = etree.SubElement(xml_exclude, "source")
                xml_source.text = event.replace(' ', replace_whitespace)
                xml_target = etree.SubElement(xml_exclude, "target")
                xml_target.text = event_prime.replace(' ', replace_whitespace)
            if "noResponseTo" in dcr and event in dcr["noResponseTo"] and event_prime in dcr["noResponseTo"][event]:
                xml_exclude = etree.SubElement(root, "rules")
                xml_type = etree.SubElement(xml_exclude, "type")
                xml_type.text = "coresponse"
                xml_source = etree.SubElement(xml_exclude, "source")
                xml_source.text = event.replace(' ', replace_whitespace)
                xml_target = etree.SubElement(xml_exclude, "target")
                xml_target.text = event_prime.replace(' ', replace_whitespace)

        # if event in dcr['marking']['executed']:
        #     marking_exec = etree.SubElement(executed, "event")
        #     marking_exec.set("id", event)
        # if event in dcr['marking']['included']:
        #     marking_incl = etree.SubElement(included, "event")
        #     marking_incl.set("id", event)
        # if event in dcr['marking']['pending']:
        #     marking_pend = etree.SubElement(pendingResponse,"event")
        #     marking_pend.set("id",event)


def export_dcr_xml(dcr, output_file_name, dcr_title='DCR from pm4py', dcr_description=None,replace_whitespace=''):
    '''
    Writes a DCR graph object to disk in the ``.xml`` file format (exported as ``.xml`` file).
    The file can be imported and visualised in the DCR solutions portal (https://dcrgraphs.net/)

    Parameters
    -----------
    dcr
        the DCR graph
    output_file_name
        dcrxml file name
    dcr_title
        title of the DCR graph
    dcr_description
        description of the DCR graph
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

    if 'subprocesses' in dcr:
        parents_dict = {}
        for sp_name, sp_events in dcr['subprocesses'].items():
            xml_event = etree.SubElement(root, "events")
            xml_event_id = etree.SubElement(xml_event, "id")
            xml_event_id.text = sp_name
            xml_event_label = etree.SubElement(xml_event, "label")
            xml_event_label.text = sp_name
            xml_event_type = etree.SubElement(xml_event, "type")
            xml_event_type.text = "subprocess"  # TODO: try "nesting" if subprocess doesn't work
            for sp_event in sp_events:
                parents_dict[sp_event] = sp_name
        export_dcr_graph(dcr, root, parents_dict, replace_whitespace=replace_whitespace)
    else:
        export_dcr_graph(dcr, root, None, replace_whitespace=replace_whitespace)

    tree = etree.ElementTree(root)
    tree.write(output_file_name, pretty_print=True)
