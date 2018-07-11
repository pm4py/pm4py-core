import xml.etree.ElementTree as xml_parser
import re
import pm4py.log.instance as log_instance
from dateutil import parser as date_parser


def import_from_path_xes(path):
    xes_tree = xml_parser.parse(path)
    root = xes_tree.getroot()

    # fix to handle the possible name space in the .xes file
    ns = re.match('\{.*\}', root.tag)
    ns = ns.group(0) if ns else ''

    log = log_instance.TraceLog({'origin': 'xes'}, [])
    for xes_trace in root.findall(ns+'trace'):
        trace_attr = __parse_attribute(xes_trace, ns+'int', int, {})
        trace_attr = __parse_attribute(xes_trace, ns+'string', str, trace_attr)
        trace_attr = __parse_attribute(xes_trace, ns+'float', float, trace_attr)
        trace_attr = __parse_attribute(xes_trace, ns+'boolean', bool, trace_attr)
        trace_attr = __parse_attribute(xes_trace, ns+'date', date_parser.parse, trace_attr)
        trace = log_instance.Trace(trace_attr,[])
        for xes_event in xes_trace.findall(ns+'event'):
            event = log_instance.Event()
            event = __parse_attribute(xes_event, ns+'int', int, event)
            event = __parse_attribute(xes_event, ns+'string', str, event)
            event = __parse_attribute(xes_event, ns+'float', float, event)
            event = __parse_attribute(xes_event, ns+'boolean', bool, event)
            event = __parse_attribute(xes_event, ns+'date', date_parser.parse, event)
            trace.append(event)
        log.append(trace)


def __parse_attribute(elem, child, type, res_attr):
    for a in elem.findall(child):
        res_attr[a.attrib['key']] = type(a.attrib['value'])
    return res_attr
