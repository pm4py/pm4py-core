import isodate

from pm4py.util import constants
from copy import deepcopy
from pm4py.objects.dcr.obj import Relations

I = Relations.I.value
E = Relations.E.value
R = Relations.R.value
N = Relations.N.value
C = Relations.C.value
M = Relations.M.value

def parse_element(curr_el, parent, dcr):
    tag = curr_el.tag.lower()
    match tag:
        case 'event':
            id = curr_el.get('id')
            if id:
                dcr['events'].add(id)
                event_type = curr_el.get('type')
                match event_type:
                    case 'subprocess':
                        dcr['subprocesses'][id] = {}
                    case _:
                        pass
                match parent.tag:
                    case 'included' | 'executed':
                        dcr['marking'][parent.tag].add(id)
                    case 'pendingResponses':
                        dcr['marking']['pending'].add(id)
                    case _:
                        pass
        case 'label':
            id = curr_el.get('id')
            dcr['labels'].add(id)
        case 'labelmapping':
            eventId = curr_el.get('eventId')
            labelId = curr_el.get('labelId')
            if labelId not in dcr['labelMapping']:
                dcr['labelMapping'][labelId] = set()
            dcr['labelMapping'][labelId].add(eventId)
        case 'condition':
            event = curr_el.get('sourceId')
            event_prime = curr_el.get('targetId')
            filter_level = curr_el.get('filterLevel')
            iso_description = curr_el.get('description')  # might have an ISO format duration
            description = None
            if iso_description:
                description = iso_description.strip()  # might have an ISO format duration
            delay = curr_el.get('time')
            groups = curr_el.get('groups')
            if not dcr['conditionsFor'].__contains__(event_prime):
                dcr['conditionsFor'][event_prime] = set()
            dcr['conditionsFor'][event_prime].add(event)

            if delay:
                if not dcr['conditionsForDelays'].__contains__(event_prime):
                    dcr['conditionsForDelays'][event_prime] = set()
                delay_days = isodate.parse_duration(delay).days
                dcr['conditionsForDelays'][event_prime].add((event, delay_days))

        case 'response':
            event = curr_el.get('sourceId')
            event_prime = curr_el.get('targetId')
            filter_level = curr_el.get('filterLevel')
            iso_description = curr_el.get('description')  # might have an ISO format duration
            description = None
            if iso_description:
                description = iso_description.strip()  # might have an ISO format duration
            deadline = curr_el.get('time')
            groups = curr_el.get('groups')
            if not dcr['responseTo'].__contains__(event):
                dcr['responseTo'][event] = set()
            dcr['responseTo'][event].add(event_prime)

            if deadline:
                if not dcr['responseToDeadlines'].__contains__(event):
                    dcr['responseToDeadlines'][event] = set()
                deadline_days = isodate.parse_duration(deadline).days
                dcr['responseToDeadlines'][event].add((event_prime, deadline_days))

        case 'include' | 'exclude':
            event = curr_el.get('sourceId')
            event_prime = curr_el.get('targetId')
            filter_level = curr_el.get('filterLevel')
            iso_description = curr_el.get('description')  # might have an ISO format duration
            description = None
            if iso_description:
                description = iso_description.strip()  # might have an ISO format duration
            deadline = curr_el.get('time')
            groups = curr_el.get('groups')
            if not dcr[f'{tag}sTo'].__contains__(event):
                dcr[f'{tag}sTo'][event] = set()
            dcr[f'{tag}sTo'][event].add(event_prime)
        case 'coresponse' | 'noresponse':
            event = curr_el.get('sourceId')
            event_prime = curr_el.get('targetId')
            filter_level = curr_el.get('filterLevel')
            iso_description = curr_el.get('description')  # might have an ISO format duration
            description = None
            if iso_description:
                description = iso_description.strip()  # might have an ISO format duration
            deadline = curr_el.get('time')
            groups = curr_el.get('groups')
            if not dcr[f'noResponseTo'].__contains__(event):
                dcr[f'noResponseTo'][event] = set()
            dcr[f'noResponseTo'][event].add(event_prime)
        case 'milestone':
            event = curr_el.get('sourceId')
            event_prime = curr_el.get('targetId')
            filter_level = curr_el.get('filterLevel')
            iso_description = curr_el.get('description')  # might have an ISO format duration
            description = None
            if iso_description:
                description = iso_description.strip()  # might have an ISO format duration
            deadline = curr_el.get('time')
            groups = curr_el.get('groups')
            if not dcr[f'{tag}sFor'].__contains__(event_prime):
                dcr[f'{tag}sFor'][event_prime] = set()
            dcr[f'{tag}sFor'][event_prime].add(event)
        case _:
            pass
    for child in curr_el:
        dcr = parse_element(child, curr_el, dcr)

    return dcr

def import_xml_tree_from_root(root, white_space_replacement=None):
    dcr = {
        'events': set(),
        'labels': set(),
        'labelMapping': {},  # this is a dictionary with one label and 1 to many events
        'conditionsFor': {},# this should be a dict with events as keys and sets as values
        'milestonesFor': {},
        'responseTo': {},
        'noResponseTo': {},
        'includesTo': {},
        'excludesTo': {},
        'conditionsForDelays': {},  # this should be a dict with events as keys and tuples as values
        'responseToDeadlines': {},
        'marking': {'executed': set(),
                    'included': set(),
                    'pending': set()
                    },
        'subprocesses': {}
    }
    dcr = parse_element(root, None, dcr)
    dcr = clean_input(dcr, white_space_replacement)
    return dcr


def clean_input(dcr, white_space_replacement=None):
    if white_space_replacement is None:
        white_space_replacement = ' '
    # remove all space characters and put conditions an milestones in the correct order (according to the actual arrows)
    for k, v in deepcopy(dcr).items():
        if k in [I, E, C, R, M, N]:
            v_new = {}
            for k2, v2 in v.items():
                v_new[k2.strip().replace(' ', '')] = set([v3.strip().replace(' ', white_space_replacement) for v3 in v2])
            dcr[k] = v_new
        elif k in ['conditionsForDelays', 'responseToDeadlines']:
            v_new = {}
            for k2, v2 in v.items():
                v_new[k2.strip().replace(' ', '')] = set([(v3.strip().replace(' ', white_space_replacement),d) for (v3,d) in v2])
            dcr[k] = v_new
        elif k == 'marking':
            for k2 in ['executed', 'included', 'pending']:
                new_v = set([v2.strip().replace(' ', white_space_replacement) for v2 in dcr[k][k2]])
                dcr[k][k2] = new_v
        elif k in ['subprocesses', 'labelMapping']:
            v_new = {}
            for k2, v2 in v.items():
                v_new[k2.strip().replace(' ', '')] = set([v3.strip().replace(' ', white_space_replacement) for v3 in v2])
            dcr[k] = v_new
        else:
            new_v = set([v2.strip().replace(' ', white_space_replacement) for v2 in dcr[k]])
            dcr[k] = new_v
    return dcr


def apply(path, parameters=None):
    if parameters is None:
        parameters = {}

    from lxml import etree, objectify

    parser = etree.XMLParser(remove_comments=True)
    xml_tree = objectify.parse(path, parser=parser)

    return import_xml_tree_from_root(xml_tree.getroot())


def import_from_string(dcr_string, parameters=None):
    if parameters is None:
        parameters = {}

    if type(dcr_string) is str:
        dcr_string = dcr_string.encode(constants.DEFAULT_ENCODING)

    from lxml import etree, objectify

    parser = etree.XMLParser(remove_comments=True)
    root = objectify.fromstring(dcr_string, parser=parser)

    return import_xml_tree_from_root(root)