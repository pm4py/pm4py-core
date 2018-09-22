from lxml import etree
from pm4py.entities.log import log as log_instance
from pm4py.entities.log import transform as log_transform
from pm4py.entities.log.util import xes as xes_util

# defines correspondence between Python types and XES types
TYPE_CORRESPONDENCE = {
    "str": xes_util.TAG_STRING,
    "int": xes_util.TAG_INT,
    "float": xes_util.TAG_FLOAT,
    "datetime": xes_util.TAG_DATE,
    "bool": xes_util.TAG_BOOLEAN,
    "dict": xes_util.TAG_LIST
}
# if a type is not found in the previous list, then default to string
DEFAULT_TYPE = xes_util.TAG_STRING


def get_XES_attr_type(attrType):
    """
    Transform a Python attribute type (e.g. str, datetime) into a XES attribute type (e.g. string, date)

    Parameters
    ----------
    attrType:
        Python attribute type
    """
    if attrType in TYPE_CORRESPONDENCE:
        attrTypeXES = TYPE_CORRESPONDENCE[attrType]
    else:
        attrTypeXES = DEFAULT_TYPE
    return attrTypeXES


def get_XES_attr_value(attrValue, attrTypeXES):
    """
    Transform an attribute value from Python format to XES format (the type is provided as argument)

    Parameters
    ----------
    attrValue:
        XES attribute value
    attrTypeXES:
        XES attribute type

    """
    if attrTypeXES == xes_util.TAG_DATE:
        defaultDateRepr = attrValue.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3] + attrValue.strftime('%z')[
                                                                            0:3] + ":" + attrValue.strftime('%z')[3:5]
        return defaultDateRepr.replace(" ", "T")
    return str(attrValue)


def export_attributes(log, root):
    """
    Export XES attributes (at the log level) from a PM4PY trace log

    Parameters
    ----------
    log: :class:`pm4py.log.log.TraceLog`
        PM4PY trace log
    root:
        Output XML root element

    """
    export_attributes_element(log, root)


def export_extensions(log, root):
    """
    Export XES extensions from a PM4PY trace log

    Parameters
    ----------
    log: :class:`pm4py.log.log.TraceLog`
        PM4PY trace log
    root:
        Output XML root element

    """
    for ext in log.extensions.keys():
        extValue = log.extensions[ext]
        logExtension = etree.SubElement(root, xes_util.TAG_EXTENSION)
        if not ext is None and not extValue[xes_util.KEY_PREFIX] is None and not extValue[xes_util.KEY_URI] is None:
            logExtension.set(xes_util.KEY_NAME, ext)
            logExtension.set(xes_util.KEY_PREFIX, extValue[xes_util.KEY_PREFIX])
            logExtension.set(xes_util.KEY_URI, extValue[xes_util.KEY_URI])


def export_globals(log, root):
    """
    Export XES globals from a PM4PY trace log

    Parameters
    ----------
    log: :class:`pm4py.log.log.TraceLog`
        PM4PY trace log
    root:
        Output XML root element

    """
    for glob in log.omni_present.keys():
        globEls = log.omni_present[glob]
        xesGlobal = etree.SubElement(root, xes_util.TAG_GLOBAL)
        export_attributes_element(globEls, xesGlobal)


def export_classifiers(log, root):
    """
    Export XES classifiers from a PM4PY trace log

    Parameters
    ----------
    log: :class:`pm4py.log.log.TraceLog`
        PM4PY trace log
    root:
        Output XML root element

    """
    for clas in log.classifiers.keys():
        clasValue = log.classifiers[clas]
        classifier = etree.SubElement(root, xes_util.TAG_CLASSIFIER)
        classifier.set(xes_util.KEY_NAME, clas)
        classifier.set(xes_util.KEY_KEYS, " ".join(clasValue))


def export_attributes_element(logElement, xmlElement):
    """
    Export attributes related to a single element

    Parameters
    ----------
    logElement:
        Element in trace log (event, trace ...)
    xmlElement:
        XML element
    """
    if hasattr(logElement, "attributes"):
        logElement = logElement.attributes

    for attr in logElement:
        if attr is not None:
            attrType = type(logElement[attr]).__name__
            attrTypeXES = get_XES_attr_type(attrType)
            if attrType is not None and attrTypeXES is not None:
                if attrTypeXES == xes_util.TAG_LIST:
                    if logElement[attr]['value'] is None:
                        thisAttribute = etree.SubElement(xmlElement, attrTypeXES)
                        thisAttribute.set(xes_util.KEY_KEY, attr)
                        thisAttributeValues = etree.SubElement(thisAttribute, "values")
                        export_attributes_element(logElement[attr]['children'], thisAttributeValues)
                    else:
                        attrType = type(logElement[attr]['value']).__name__
                        attrTypeXES = get_XES_attr_type(attrType)
                        if attrType is not None and attrTypeXES is not None:
                            attrValue = logElement[attr]['value']
                            if attrValue is not None:
                                thisAttribute = etree.SubElement(xmlElement, attrTypeXES)
                                thisAttribute.set(xes_util.KEY_KEY, attr)
                                thisAttribute.set(xes_util.KEY_VALUE, str(logElement[attr]['value']))
                                export_attributes_element(logElement[attr]['children'], thisAttribute)
                else:
                    attrValue = get_XES_attr_value(logElement[attr], attrTypeXES)
                    if attrValue is not None:
                        thisAttribute = etree.SubElement(xmlElement, attrTypeXES)
                        thisAttribute.set(xes_util.KEY_KEY, attr)
                        thisAttribute.set(xes_util.KEY_VALUE, str(attrValue))


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
    Export XES traces from a PM4PY trace log

    Parameters
    ----------
    log: :class:`pm4py.log.log.TraceLog`
        PM4PY trace log
    root:
        Output XML root element

    """
    for tr in log:
        trace = etree.SubElement(root, xes_util.TAG_TRACE)
        export_attributes_element(tr, trace)
        export_traces_events(tr, trace)


def export_log_tree(log):
    """
    Get XES log XML tree from a PM4Py trace log

    Parameters
    -----------
    log
        PM4Py trace log

    Returns
    -----------
    tree
        XML tree
    """
    # If the log is in log_instance.EventLog, then transform it into log_instance.TraceLog format
    if type(log) is log_instance.EventLog:
        log = log_transform.transform_event_log_to_trace_log(log)
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
    Export a trace log into a string

    Parameters
    -----------
    log: :class:`pm4py.log.log.TraceLog`
        PM4PY trace log
    parameters
        Parameters of the algorithm

    Returns
    -----------
    logString
        Log as a string
    """
    if parameters is None:
        parameters = {}

    # Gets the XML tree to export
    tree = export_log_tree(log)

    return etree.tostring(tree, xml_declaration=True, encoding="utf-8", pretty_print=True)


def export_log(log, outputFilePath, parameters=None):
    """
    Export XES log from a PM4PY trace log

    Parameters
    ----------
    log: :class:`pm4py.log.log.TraceLog`
        PM4PY trace log
    outputFilePath:
        Output file path
    parameters
        Parameters of the algorithm

    """
    if parameters is None:
        parameters = {}

    # Gets the XML tree to export
    tree = export_log_tree(log)
    # Effectively do the export of the event log
    tree.write(outputFilePath, pretty_print=True, xml_declaration=True, encoding="utf-8")