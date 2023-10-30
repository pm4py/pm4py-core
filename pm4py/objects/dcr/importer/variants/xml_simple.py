from lxml import etree
from datetime import datetime, timedelta


def import_dcr_xml(xml_file, replace_whitespace=''):
    tree = etree.parse(xml_file)
    root = tree.getroot()

    dcr_template = {
        'events': set(),
        'conditionsFor': {},
        'milestonesFor': {},
        'responseTo': {},
        'noResponseTo': {},
        'includesTo': {},
        'excludesTo': {},
        'marking': {'executed': set(),
                    'included': set(),
                    'pending': set(),
                    'executedTime': {},
                    'pendingDeadline': {}},
        'conditionsForDelays': {},
        'responseToDeadlines': {},
        'subprocesses': {},
        'nestings': {},
        'labels': set(),
        'labelMapping': {},
        'roles': set(),
        'roleAssignments': {},
        'readRoleAssignments': {}
    }

    for event_elem in root.findall('.//events'):
        event_id = event_elem.find('id').text.replace(' ', replace_whitespace)
        dcr_template['events'].add(event_id)
        dcr_template['marking']['included'].add(event_id)

    for rule_elem in root.findall('.//rules'):
        rule_type = rule_elem.find('type').text
        source = rule_elem.find('source').text.replace(' ', replace_whitespace)
        target = rule_elem.find('target').text.replace(' ', replace_whitespace)

        if rule_type == 'condition':
            if 'conditionsFor' not in dcr_template:
                dcr_template['conditionsFor'] = {}
            if target not in dcr_template['conditionsFor']:
                dcr_template['conditionsFor'][target] = set()
            dcr_template['conditionsFor'][target].add(source)

            # Handle duration
            duration_elem = rule_elem.find('duration')
            if duration_elem is not None:
                duration = timedelta(seconds=float(duration_elem.text))
                if 'conditionsForDelays' not in dcr_template:
                    dcr_template['conditionsForDelays'] = {}
                if target not in dcr_template['conditionsForDelays']:
                    dcr_template['conditionsForDelays'][target] = {}
                dcr_template['conditionsForDelays'][target][source] = duration

        elif rule_type == 'response':
            if 'responseTo' not in dcr_template:
                dcr_template['responseTo'] = {}
            if source not in dcr_template['responseTo']:
                dcr_template['responseTo'][source] = set()
            dcr_template['responseTo'][source].add(target)

            # Handle duration
            duration_elem = rule_elem.find('duration')
            if duration_elem is not None:
                duration = timedelta(seconds=float(duration_elem.text))
                if 'responseToDeadlines' not in dcr_template:
                    dcr_template['responseToDeadlines'] = {}
                if source not in dcr_template['responseToDeadlines']:
                    dcr_template['responseToDeadlines'][source] = {}
                dcr_template['responseToDeadlines'][source][target] = duration

        elif rule_type == 'include':
            if 'includesTo' not in dcr_template:
                dcr_template['includesTo'] = {}
            if source not in dcr_template['includesTo']:
                dcr_template['includesTo'][source] = set()
            dcr_template['includesTo'][source].add(target)

        elif rule_type == 'exclude':
            if 'excludesTo' not in dcr_template:
                dcr_template['excludesTo'] = {}
            if source not in dcr_template['excludesTo']:
                dcr_template['excludesTo'][source] = set()
            dcr_template['excludesTo'][source].add(target)

        elif rule_type == 'milestone':
            if 'milestonesFor' not in dcr_template:
                dcr_template['milestonesFor'] = {}
            if target not in dcr_template['milestonesFor']:
                dcr_template['milestonesFor'][target] = set()
            dcr_template['milestonesFor'][target].add(source)

        elif rule_type == 'coresponse':
            if 'noResponseTo' not in dcr_template:
                dcr_template['noResponseTo'] = {}
            if source not in dcr_template['noResponseTo']:
                dcr_template['noResponseTo'][source] = set()
            dcr_template['noResponseTo'][source].add(target)

    return dcr_template