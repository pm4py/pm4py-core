from lxml import etree

from pm4py.objects.conversion.log import factory as log_converter
from pm4py.objects.log import log as log_instance
from pm4py.util import xes_constants as xes_util

# defines correspondence between Python types and XES types
TYPE_CORRESPONDENCE = {
    "str": xes_util.TAG_STRING,
    "int": xes_util.TAG_INT,
    "float": xes_util.TAG_FLOAT,
    "datetime": xes_util.TAG_DATE,
    "Timestamp": xes_util.TAG_DATE,
    "bool": xes_util.TAG_BOOLEAN,
    "dict": xes_util.TAG_LIST
}
# if a type is not found in the previous list, then default to string
DEFAULT_TYPE = xes_util.TAG_STRING


def get_xes_attr_type(attr_type):
    """
    Transform a Python attribute type (e.g. str, datetime) into a XES attribute type (e.g. string, date)

    Parameters
    ----------
    attr_type:
        Python attribute type
    """
    if attr_type in TYPE_CORRESPONDENCE:
        attr_type_xes = TYPE_CORRESPONDENCE[attr_type]
    else:
        attr_type_xes = DEFAULT_TYPE
    return attr_type_xes


def get_xes_attr_value(attr_value, attr_type_xes):
    """
    Transform an attribute value from Python format to XES format (the type is provided as argument)

    Parameters
    ----------
    attr_value:
        XES attribute value
    attr_type_xes:
        XES attribute type

    """
    if attr_type_xes == xes_util.TAG_DATE:
        if attr_value.strftime('%z') and len(attr_value.strftime('%z')) >= 5:
            default_date_repr = attr_value.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3] + attr_value.strftime('%z')[
                                                                                   0:3] + ":" + attr_value.strftime(
                '%z')[
                                                                                                3:5]
        else:
            default_date_repr = attr_value.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3] + "+00:00"
        return default_date_repr.replace(" ", "T")
    elif attr_type_xes == xes_util.TAG_BOOLEAN:
        return str(attr_value).lower()
    return str(attr_value)


def export_attributes(log, root):
    """
    Export XES attributes (at the log level) from a PM4PY log

    Parameters
    ----------
    log: :class:`pm4py.log.log.EventLog`
        PM4PY log
    root:
        Output XML root element

    """
    export_attributes_element(log, root)


def export_extensions(log, root):
    """
    Export XES extensions from a PM4PY log

    Parameters
    ----------
    log: :class:`pm4py.log.log.EventLog`
        PM4PY log
    root:
        Output XML root element

    """
    for ext in log.extensions.keys():
        ext_value = log.extensions[ext]
        log_extension = etree.SubElement(root, xes_util.TAG_EXTENSION)
        if ext is not None and not ext_value[xes_util.KEY_PREFIX] is None and ext_value[xes_util.KEY_URI] is not None:
            log_extension.set(xes_util.KEY_NAME, ext)
            log_extension.set(xes_util.KEY_PREFIX, ext_value[xes_util.KEY_PREFIX])
            log_extension.set(xes_util.KEY_URI, ext_value[xes_util.KEY_URI])


def export_globals(log, root):
    """
    Export XES globals from a PM4PY log

    Parameters
    ----------
    log: :class:`pm4py.log.log.EventLog`
        PM4PY log
    root:
        Output XML root element

    """
    for glob in log.omni_present.keys():
        glob_els = log.omni_present[glob]
        xes_global = etree.SubElement(root, xes_util.TAG_GLOBAL)
        xes_global.set(xes_util.KEY_SCOPE, glob)
        export_attributes_element(glob_els, xes_global)


def export_classifiers(log, root):
    """
    Export XES classifiers from a PM4PY log

    Parameters
    ----------
    log: :class:`pm4py.log.log.EventLog`
        PM4PY log
    root:
        Output XML root element

    """
    for clas in log.classifiers.keys():
        clas_value = log.classifiers[clas]
        classifier = etree.SubElement(root, xes_util.TAG_CLASSIFIER)
        classifier.set(xes_util.KEY_NAME, clas)
        values_spaces = [(" " in x) for x in clas_value]
        values_spaces = [x for x in values_spaces if x]
        if len(values_spaces) > 0:
            clas_value = ["'" + x + "'" for x in clas_value]
        classifier.set(xes_util.KEY_KEYS, " ".join(clas_value))


def export_attributes_element(log_element, xml_element):
    """
    Export attributes related to a single element

    Parameters
    ----------
    log_element:
        Element in log (event, trace ...)
    xml_element:
        XML element
    """
    if hasattr(log_element, "attributes"):
        log_element = log_element.attributes

    for attr in log_element:
        if attr is not None:
            attr_type = type(log_element[attr]).__name__
            attr_type_xes = get_xes_attr_type(attr_type)
            if attr_type is not None and attr_type_xes is not None:
                if attr_type_xes == xes_util.TAG_LIST:
                    if log_element[attr]['value'] is None:
                        this_attribute = etree.SubElement(xml_element, attr_type_xes)
                        this_attribute.set(xes_util.KEY_KEY, attr)
                        this_attribute_values = etree.SubElement(this_attribute, "values")
                        export_attributes_element(log_element[attr]['children'], this_attribute_values)
                    else:
                        attr_type = type(log_element[attr]['value']).__name__
                        attr_type_xes = get_xes_attr_type(attr_type)
                        if attr_type is not None and attr_type_xes is not None:
                            attr_value = log_element[attr]['value']
                            if attr_value is not None:
                                this_attribute = etree.SubElement(xml_element, attr_type_xes)
                                this_attribute.set(xes_util.KEY_KEY, attr)
                                this_attribute.set(xes_util.KEY_VALUE, str(log_element[attr]['value']))
                                export_attributes_element(log_element[attr]['children'], this_attribute)
                else:
                    attr_value = get_xes_attr_value(log_element[attr], attr_type_xes)
                    if attr_value is not None:
                        this_attribute = etree.SubElement(xml_element, attr_type_xes)
                        this_attribute.set(xes_util.KEY_KEY, attr)
                        this_attribute.set(xes_util.KEY_VALUE, str(attr_value))


def export_traces_events(tr, trace):
    """
    Export XES events given a PM4PY trace

    Parameters
    ----------
    tr: :class:`pm4py.log.log.Trace`
        PM4PY trace
    trace:
        Output XES trace

    """

    for ev in tr:
        event = etree.SubElement(trace, xes_util.TAG_EVENT)
        export_attributes_element(ev, event)


def export_traces(log, root):
    """
    Export XES traces from a PM4PY log

    Parameters
    ----------
    log: :class:`pm4py.log.log.EventLog`
        PM4PY log
    root:
        Output XML root element

    """
    for tr in log:
        trace = etree.SubElement(root, xes_util.TAG_TRACE)
        export_attributes_element(tr, trace)
        export_traces_events(tr, trace)


def export_log_tree(log):
    """
    Get XES log XML tree from a PM4Py log

    Parameters
    -----------
    log
        PM4Py log

    Returns
    -----------
    tree
        XML tree
    """
    # If the log is in log_instance.EventStream, then transform it into log_instance.EventLog format
    if type(log) is log_instance.EventStream:
        log = log_converter.apply(log)
    root = etree.Element(xes_util.TAG_LOG)

    # add attributes at the log level
    export_attributes(log, root)
    # add extensions at the log level
    export_extensions(log, root)
    # add globals at the log level
    export_globals(log, root)
    # add classifiers at the log level
    export_classifiers(log, root)
    # add traces at the log level
    export_traces(log, root)

    tree = etree.ElementTree(root)

    return tree


def export_log_as_string(log, parameters=None):
    """
    Export a log into a string

    Parameters
    -----------
    log: :class:`pm4py.log.log.EventLog`
        PM4PY log
    parameters
        Parameters of the algorithm

    Returns
    -----------
    logString
        Log as a string
    """
    if parameters is None:
        parameters = {}
    del parameters

    # Gets the XML tree to export
    tree = export_log_tree(log)

    return etree.tostring(tree, xml_declaration=True, encoding="utf-8", pretty_print=True)


def export_log(log, output_file_path, parameters=None):
    """
    Export XES log from a PM4PY log

    Parameters
    ----------
    log: :class:`pm4py.log.log.EventLog`
        PM4PY log
    output_file_path:
        Output file path
    parameters
        Parameters of the algorithm

    """
    if parameters is None:
        parameters = {}
    del parameters

    # Gets the XML tree to export
    tree = export_log_tree(log)
    # Effectively do the export of the event log
    tree.write(output_file_path, pretty_print=True, xml_declaration=True, encoding="utf-8")
