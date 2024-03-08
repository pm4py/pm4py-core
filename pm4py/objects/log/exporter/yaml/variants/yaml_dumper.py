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
import gzip
import importlib.util
from enum import Enum
import math
import numbers

from pm4py.objects.log.util import xes as xes_util
from pm4py.util import exec_utils, constants, xes_constants
import yaml
from yaml.cyaml import CDumper, CSafeDumper
from yaml import Dumper, SafeDumper


class DumperType(Enum):
    C_DUMPER = CDumper
    C_SAFE_DUMPER = CSafeDumper
    SAFE_DUMPER = SafeDumper
    DUMPER = Dumper


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
    "numpy.datetime64": xes_util.TAG_DATE,
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


def export_log(log, fp_obj, encoding, variant, parameters=None, log_header=None, append=False):
    """
    Exports the contents of the log line-by-line
    to a file object

    Parameters
    --------------
    log
        Event log
    fp_obj
        File object
    encoding
        Encoding
    variant
        YAML Dumper variant
    parameters
        Parameters
    """

    show_progress_bar = exec_utils.get_param_value(
        Parameters.SHOW_PROGRESS_BAR, parameters, constants.SHOW_PROGRESS_BAR
    )
    progress = None

    if importlib.util.find_spec("tqdm") and show_progress_bar:
        from tqdm.auto import tqdm

        progress = tqdm(
            total=get_yaml_num_events(log), desc="exporting log, completed traces :: "
        )

    # in case log_header is not given as parameter
    if log_header is None:
        log_header = dict({xes_constants.TAG_LOG: dict()})

        log_header[xes_constants.TAG_LOG]["xes"] = {
            "creator": "cpee.org",
            "features": "nested-attributes",
        }

        log_header[xes_constants.TAG_LOG][xes_constants.TAG_EXTENSION] = dict()
        for ext_key, ext_value in log.extensions.items():
            log_header[xes_constants.TAG_LOG][xes_constants.TAG_EXTENSION][
                ext_key
            ] = ext_value

        log_header[xes_constants.TAG_LOG][xes_constants.TAG_CLASSIFIER] = dict()
        for class_name, class_attributes in log.classifiers.items():
            log_header[xes_constants.TAG_LOG][xes_constants.TAG_CLASSIFIER][
                class_name
            ] = class_attributes

        log_header[xes_constants.TAG_LOG][xes_constants.TAG_GLOBAL] = dict()
        for scope in log.omni_present:
            log_header[xes_constants.TAG_LOG][xes_constants.TAG_GLOBAL][scope] = dict()
            for attr_name, attr_value in log.omni_present[scope].items():
                log_header[xes_constants.TAG_LOG][xes_constants.TAG_GLOBAL][scope][
                    attr_name
                ] = attr_value

        for att_key, att_value in log.attributes.items():
            log_header[xes_constants.TAG_LOG][att_key] = export_attribute(
                att_key, att_value
            )

    if not append:
        yaml.dump(
            log_header,
            fp_obj,
            encoding=encoding,
            default_flow_style=False,
            Dumper=variant.value,
        )

    for trace in log:
        trace_obj = dict({xes_constants.TAG_TRACE: dict()})
        for trace_att_key, trace_att_value in trace.attributes.items():
            if isinstance(trace_att_value, numbers.Number) and math.isnan(
                trace_att_value
            ):
                continue

            if trace_att_key == xes_util.DEFAULT_TIMESTAMP_KEY and not isinstance(
                trace_att_value, str
            ):
                trace_obj[xes_constants.TAG_TRACE][trace_att_key] = str(
                    trace_att_value.isoformat()
                )

            else:
                exported_attribute = export_attribute(trace_att_key, trace_att_value)
                trace_obj[xes_constants.TAG_TRACE][trace_att_key] = exported_attribute

        # XES-YAML normal form consists of only 1 trace => no need to record the trace
        # => in case of multiple traces, record them
        if len(log) > 1 and trace_obj[xes_constants.TAG_TRACE] != {}:
            fp_obj.write("---\n".encode(encoding))
            yaml.dump(
                trace_obj,
                fp_obj,
                encoding=encoding,
                default_flow_style=False,
                Dumper=variant.value,
            )

        for event in trace:
            event_obj = dict({xes_constants.TAG_EVENT: dict()})
            for event_att_key, event_att_value in event.items():
                if isinstance(event_att_value, numbers.Number) and math.isnan(
                    event_att_value
                ):
                    continue

                if event_att_key == xes_util.DEFAULT_TIMESTAMP_KEY and not isinstance(
                    event_att_value, str
                ):
                    event_obj[xes_constants.TAG_EVENT][event_att_key] = str(
                        event_att_value.isoformat()
                    )

                else:
                    exported_attribute = export_attribute(
                        event_att_key, event_att_value
                    )
                    event_obj[xes_constants.TAG_EVENT][
                        event_att_key
                    ] = exported_attribute

            fp_obj.write("---\n".encode(encoding))
            yaml.dump(
                event_obj,
                fp_obj,
                encoding=encoding,
                default_flow_style=False,
                Dumper=variant.value,
            )

            if progress is not None:
                progress.update()

    # gracefully close progress bar
    if progress is not None:
        progress.close()
    del progress, log


def export_attribute(attr_key, attr_value):
    if attr_key is None or attr_value is None:
        return ""

    attr_type = __get_xes_attr_type(attr_key, type(attr_value).__name__)

    if not attr_type == xes_util.TAG_LIST:
        # simple attribute
        return attr_value

    else:
        if attr_value[xes_util.KEY_VALUE] is None:
            # list
            attr_list = list()

            for subbattr in attr_value[xes_util.KEY_CHILDREN]:
                if isinstance(subbattr, tuple):
                    if subbattr[0] == "":
                        attr_list.append(export_attribute("", subbattr[1]))

                    else:
                        attr_list.append(
                            {subbattr[0]: export_attribute("", subbattr[1])}
                        )
                else:
                    attr_list.append(subbattr)

            return attr_list

        else:
            # nested attribute
            attr_dict = dict()
            for subattr_key, subattr_value in attr_value[xes_util.KEY_CHILDREN].items():
                attr_dict[subattr_key] = export_attribute(subattr_key, subattr_value)

            return attr_dict


def apply(
    log,
    output_file_path,
    variant: DumperType,
    parameters=None,
    append=False,
    log_header=None,
):
    """
    Exports a XES log using a non-standard exporter
    (classifiers, lists, nested attributes, globals, extensions are not supported)

    Parameters
    ------------
    log
        Event log
    output_file_path
        Path to the XES file
    parameters
        Parameters
    """

    if parameters is None:
        parameters = {}

    encoding = exec_utils.get_param_value(
        Parameters.ENCODING, parameters, constants.DEFAULT_ENCODING
    )
    compress = exec_utils.get_param_value(
        Parameters.COMPRESS, parameters, output_file_path.lower().endswith(".gz")
    )

    if compress:
        if not output_file_path.lower().endswith(".gz"):
            output_file_path = output_file_path + ".gz"
        f = gzip.open(output_file_path, mode="ab" if append else "wb")
    else:
        f = open(output_file_path, "ab" if append else "wb")

    export_log(
        log,
        f,
        encoding,
        variant,
        parameters=parameters,
        log_header=log_header,
        append=append,
    )

    f.close()



def get_yaml_num_events(log):
    total_events = 0
    for trace in log:
        for _ in trace:
            total_events += 1
    return total_events


# does require less memory than dump_all
# but only tested for small files
# TODO: do for larger files
def append_log(log, fp_obj, encoding, parameters=None):
    total_events = get_yaml_num_events(log)

    show_progress_bar = exec_utils.get_param_value(
        Parameters.SHOW_PROGRESS_BAR, parameters, constants.SHOW_PROGRESS_BAR
    )
    progress = None

    if importlib.util.find_spec("tqdm") and show_progress_bar:
        from tqdm.auto import tqdm

        progress = tqdm(total=total_events, desc="exporting log, completed traces :: ")

    for trace in log:
        for event in trace:
            event_obj = dict({xes_constants.TAG_EVENT: dict()})

            for key, value in event.items():
                if isinstance(value, numbers.Number) and math.isnan(value):
                    continue

                # if value is None:
                #     print(f"None value for key {key}")

                if key == xes_util.DEFAULT_TIMESTAMP_KEY:
                    event_obj[xes_constants.TAG_EVENT][key] = value.isoformat()

                else:
                    event_obj[xes_constants.TAG_EVENT][key] = value

            fp_obj.write("---\n".encode(encoding))
            yaml.dump(event_obj, fp_obj, encoding=encoding, default_flow_style=False)

            if progress is not None:
                progress.update()

    # gracefully close progress bar
    if progress is not None:
        progress.close()
    del progress, log
