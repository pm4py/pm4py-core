import os.path
from lxml import etree


def create_artificial_event_log_as_xes_file(path, file_name, traces, force=False):
    """
    Creates an simple, artificial event log file in the .xes format based on provided traces

    :param path: path where event log gets stored
    :param file_name: name of the .xes file that will be generated
    :param traces: list of dicts with properties:
                                                    -frequency (how often the trace occurs)
                                                    -events: list of strings representing the event name
    :param force: if true and the filename already exists in provided path, the file will be overwritten
    :return: true if event_log_file was written
    """
    file_exists = os.path.isfile(os.path.join(path, file_name) + '.xes')
    if not file_exists or (file_exists and force):
        f = open(os.path.join(path, file_name) + '.xes', "w+")
        f.write(create_xes_string(traces))
        return True
    return False


def create_xes_string(traces):
    """
    Given the trace information (:param traces) this function returns a string that represents the traces in the XES
    format that can be directly stored into a .xes file.
    :param traces: <class 'list'>, e.g.: [{'frequency': 40, 'events': ['A', 'B', 'C']}, ...]
    :return: 'str'
    """
    l = etree.Element('log')
    trace_count = 1
    for trace in traces:
        for i in range(trace['frequency']):
            t = etree.SubElement(l, 'trace')
            t_id = etree.SubElement(t, 'string')
            t_id.attrib['key'] = "concept:name"
            t_id.attrib['value'] = str("trace_" + str(trace_count))
            for event in trace['events']:
                e = etree.SubElement(t, 'event')
                activity_name = etree.SubElement(e, 'string')
                activity_name.attrib['key'] = 'concept:name'
                activity_name.attrib['value'] = event
            trace_count += 1
    return etree.tostring(l, pretty_print=False, method='xml', xml_declaration=True, encoding='UTF-8').decode('utf-8')


if __name__ == '__main__':
    # example of usage
    log = [
        {"frequency": 10, "events": ["A", "B", "C"]},
        {"frequency": 2, "events": ["A", "B", "B"]}
    ]
    create_artificial_event_log_as_xes_file(os.path.dirname(os.path.realpath(__file__)), 'test_log', log, force=True)
