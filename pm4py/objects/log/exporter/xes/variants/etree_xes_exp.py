'''
    This file is part of PM4Py (More Info: https://pm4py.fit.fraunhofer.de).

    PM4Py is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    PM4Py is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with PM4Py.  If not, see <https://www.gnu.org/licenses/>.
'''
import importlib.util
from enum import Enum

try:
    # do not compromise anymore importing the XES "exporter" package if "lxml" is / cannot be installed,
    # and this variant cannot be used.
    # after all, the default variant is now the "line_by_line" one.
    from lxml import etree
except:
    pass

from pm4py.objects.conversion.log import converter as log_converter
from pm4py.objects.log import obj as log_instance
from pm4py.objects.log.util import xes as xes_util
from pm4py.util import constants
from pm4py.util import exec_utils
from io import BytesIO
import gzip


class Parameters(Enum):
    COMPRESS = "compress"
    SHOW_PROGRESS_BAR = "show_progress_bar"
    ENCODING = "encoding"


# defines correspondence between Python types and XES types
__TYPE_CORRESPONDENCE = {
    "str": xes_util.TAG_STRING,
    "int": xes_util.TAG_INT,
    "float": xes_util.TAG_FLOAT,
    "datetime": xes_util.TAG_DATE,
    "Timestamp": xes_util.TAG_DATE,
    "bool": xes_util.TAG_BOOLEAN,
    "dict": xes_util.TAG_LIST,
    "numpy.int64": xes_util.TAG_INT,
    "numpy.float64": xes_util.TAG_FLOAT,
    "numpy.datetime64": xes_util.TAG_DATE
}
# if a type is not found in the previous list, then default to string
__DEFAULT_TYPE = xes_util.TAG_STRING


def __get_xes_attr_type(attr_name, attr_type):
    """
    Transform a Python attribute type (e.g. str, datetime) into a XES attribute type (e.g. string, date)

    Parameters
    ----------
    attr_name
        Name of the attribute
    attr_type:
        Python attribute type
    """
    if attr_name == xes_util.DEFAULT_NAME_KEY:
        return xes_util.TAG_STRING
    elif attr_type in __TYPE_CORRESPONDENCE:
        attr_type_xes = __TYPE_CORRESPONDENCE[attr_type]
    else:
        attr_type_xes = __DEFAULT_TYPE
    return attr_type_xes


def __get_xes_attr_value(attr_value, attr_type_xes):
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
        return attr_value.isoformat()
    elif attr_type_xes == xes_util.TAG_BOOLEAN:
        return str(attr_value).lower()
    return str(attr_value)


def __export_attributes(log, root):
    """
    Export XES attributes (at the log level) from a PM4PY log

    Parameters
    ----------
    log: :class:`pm4py.log.log.EventLog`
        PM4PY log
    root:
        Output XML root element

    """
    __export_attributes_element(log, root)


def __export_extensions(log, root):
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


def __export_globals(log, root):
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
        __export_attributes_element(glob_els, xes_global)


def __export_classifiers(log, root):
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


def __export_attributes_element(log_element, xml_element):
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

    if isinstance(log_element, list) or isinstance(log_element, set):
        items = log_element
    else:
        items = log_element.items()

    for attr, attr_value in items:
        if attr is not None and attr_value is not None:
            attr_type = type(attr_value).__name__
            attr_type_xes = __get_xes_attr_type(attr, attr_type)
            if attr_type is not None and attr_type_xes is not None:
                if attr_type_xes == xes_util.TAG_LIST:
                    if attr_value['value'] is None:
                        this_attribute = etree.SubElement(xml_element, attr_type_xes)
                        this_attribute.set(xes_util.KEY_KEY, attr)
                        this_attribute_values = etree.SubElement(this_attribute, "values")
                        __export_attributes_element(attr_value['children'], this_attribute_values)
                    else:
                        attr_type = type(attr_value['value']).__name__
                        attr_type_xes = __get_xes_attr_type(attr, attr_type)
                        if attr_type is not None and attr_type_xes is not None:
                            if attr_value is not None:
                                this_attribute = etree.SubElement(xml_element, attr_type_xes)
                                this_attribute.set(xes_util.KEY_KEY, attr)
                                this_attribute.set(xes_util.KEY_VALUE, str(attr_value['value']))
                                __export_attributes_element(attr_value['children'], this_attribute)
                else:
                    attr_value = __get_xes_attr_value(attr_value, attr_type_xes)
                    if attr_value is not None:
                        this_attribute = etree.SubElement(xml_element, attr_type_xes)
                        this_attribute.set(xes_util.KEY_KEY, attr)
                        this_attribute.set(xes_util.KEY_VALUE, str(attr_value))


def __export_traces_events(tr, trace):
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
        __export_attributes_element(ev, event)


def __export_traces(log, root, parameters=None):
    """
    Export XES traces from a PM4PY log

    Parameters
    ----------
    log: :class:`pm4py.log.log.EventLog`
        PM4PY log
    root:
        Output XML root element

    """
    if parameters is None:
        parameters = {}

    show_progress_bar = exec_utils.get_param_value(Parameters.SHOW_PROGRESS_BAR, parameters, constants.SHOW_PROGRESS_BAR)

    progress = None
    if importlib.util.find_spec("tqdm") and show_progress_bar:
        from tqdm.auto import tqdm
        progress = tqdm(total=len(log), desc="exporting log, completed traces :: ")

    for tr in log:
        trace = etree.SubElement(root, xes_util.TAG_TRACE)
        __export_attributes_element(tr, trace)
        __export_traces_events(tr, trace)
        if progress is not None:
            progress.update()

    # gracefully close progress bar
    if progress is not None:
        progress.close()
    del progress


def export_log_tree(log, parameters=None):
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
        log = log_converter.apply(log, variant=log_converter.Variants.TO_EVENT_LOG, parameters=parameters)
    root = etree.Element(xes_util.TAG_LOG)
    root.set(xes_util.TAG_VERSION, xes_util.VALUE_XES_VERSION)
    root.set(xes_util.TAG_FEATURES, xes_util.VALUE_XES_FEATURES)
    root.set(xes_util.TAG_XMLNS, xes_util.VALUE_XMLNS)

    # add attributes at the log level
    __export_attributes(log, root)
    # add extensions at the log level
    __export_extensions(log, root)
    # add globals at the log level
    __export_globals(log, root)
    # add classifiers at the log level
    __export_classifiers(log, root)
    # add traces at the log level
    __export_traces(log, root, parameters=parameters)

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

    encoding = exec_utils.get_param_value(Parameters.ENCODING, parameters, constants.DEFAULT_ENCODING)
    compress = exec_utils.get_param_value(Parameters.COMPRESS, parameters, False)

    # Gets the XML tree to export
    tree = export_log_tree(log, parameters=parameters)

    b = BytesIO()

    if compress:
        d = gzip.GzipFile(fileobj=b, mode="wb")
    else:
        d = b

    tree.write(d, pretty_print=True, xml_declaration=True, encoding=encoding)

    if compress:
        d.close()

    return b.getvalue()


def __export_log(log, output_file_path, parameters=None):
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
    parameters = dict() if parameters is None else parameters

    encoding = exec_utils.get_param_value(Parameters.ENCODING, parameters, constants.DEFAULT_ENCODING)
    compress = exec_utils.get_param_value(Parameters.COMPRESS, parameters, output_file_path.lower().endswith(".gz"))

    # Gets the XML tree to export
    tree = export_log_tree(log, parameters=parameters)

    if compress:
        if not output_file_path.lower().endswith(".gz"):
            output_file_path = output_file_path + ".gz"
        f = gzip.open(output_file_path, mode="wb")
    else:
        f = open(output_file_path, "wb")

    # Effectively do the export of the event log
    tree.write(f, pretty_print=True, xml_declaration=True, encoding=encoding)

    f.close()


def apply(log, output_file_path, parameters=None):
    return __export_log(log, output_file_path, parameters)
