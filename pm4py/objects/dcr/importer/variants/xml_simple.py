import copy

import isodate

from pm4py.util import constants
from copy import deepcopy
from pm4py.objects.dcr.obj import Relations, dcr_template, DcrGraph

I = Relations.I.value
E = Relations.E.value
R = Relations.R.value
N = Relations.N.value
C = Relations.C.value
M = Relations.M.value


def parse_element(curr_el, parent, dcr):
    # Create the DCR graph
    tag = curr_el.tag.lower()
    match tag:
        case 'events':
            id = curr_el.find('id').text
            dcr['events'].add(id)
            label = curr_el.find('label').text
            dcr['labels'].add(label)
        case 'rules':
            type = curr_el.find('type').text
            source = curr_el.find('source').text
            target = curr_el.find('target').text
            match type:
                case 'condition':
                    if not dcr['conditionsFor'].get(target):
                        dcr['conditionsFor'][target] = set()
                    dcr['conditionsFor'][target].add(source)
                case 'response':
                    if not dcr['responseTo'].get(source):
                        dcr['responseTo'][source] = set()
                    dcr['responseTo'][source].add(target)
                case 'exclude':
                    if not dcr['excludesTo'].get(source):
                        dcr['excludesTo'][source] = set()
                    dcr['excludesTo'][source].add(target)
                case 'include':
                    if not dcr['includesTo'].get(source):
                        dcr['includesTo'][source] = set()
                    dcr['includesTo'][source].add(target)
        case _:
            pass
    for child in curr_el:
        dcr = parse_element(child, curr_el, dcr)

    return dcr


def import_xml_tree_from_root(root):
    dcr = copy.deepcopy(dcr_template)
    dcr = parse_element(root, None, dcr)
    '''
    Transform the dictionary into a DCR_Graph object
    '''
    graph = DcrGraph(dcr)
    return graph


def apply(path, parameters=None):
    '''
    Reads a DCR Graph from an XML file

    Parameters
    ----------
    path
        Path to the XML file

    Returns
    -------
    DCR_Graph
        DCR Graph object
    '''
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