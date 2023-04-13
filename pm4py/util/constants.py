import os
import pkgutil
from enum import Enum


def get_param_from_env(name, default):
    if name in os.environ and os.environ[name]:
        return str(os.environ[name])
    return default


PARAMETER_CONSTANT_ACTIVITY_KEY = 'pm4py:param:activity_key'
PARAMETER_CONSTANT_ATTRIBUTE_KEY = "pm4py:param:attribute_key"
PARAMETER_CONSTANT_TIMESTAMP_KEY = 'pm4py:param:timestamp_key'
PARAMETER_CONSTANT_START_TIMESTAMP_KEY = 'pm4py:param:start_timestamp_key'
PARAMETER_CONSTANT_CASEID_KEY = 'pm4py:param:case_id_key'
PARAMETER_CONSTANT_RESOURCE_KEY = 'pm4py:param:resource_key'
PARAMETER_CONSTANT_TRANSITION_KEY = 'pm4py:param:transition_key'
PARAMETER_CONSTANT_GROUP_KEY = 'pm4py:param:group_key'

GROUPED_DATAFRAME = 'grouped_dataframe'
RETURN_EA_COUNT_DICT_AUTOFILTER = 'return_ea_count_dict_autofilter'
PARAM_MOST_COMMON_VARIANT = "most_common_variant"
PARAM_MOST_COMMON_PATHS = "most_common_paths"

CASE_CONCEPT_NAME = "case:concept:name"
CASE_ATTRIBUTE_GLUE = 'case:concept:name'
CASE_ATTRIBUTE_PREFIX = 'case:'

# the following can be removed
PARAMETER_KEY_CASE_GLUE = 'case_id_glue'
PARAMETER_KEY_CASE_ATTRIBUTE_PRFIX = 'case:'

STOCHASTIC_DISTRIBUTION = "stochastic_distribution"
LAYOUT_INFORMATION_PETRI = "layout_information_petri"
PLACE_NAME_TAG = "place_name_tag"
TRANS_NAME_TAG = "trans_name_tag"

DEFAULT_VARIANT_SEP = ","
DEFAULT_INDEX_KEY = "@@index"
DEFAULT_CASE_INDEX_KEY = "@@case_index"
DEFAULT_INDEX_IN_TRACE_KEY = "@@index_in_trace"
DEFAULT_EVENT_INDEX_KEY = "@@event_index"
DEFAULT_FLOW_TIME = "@@flow_time"
DEFAULT_CLASSIFIER_ATTRIBUTE = "@@classifier"

DEFAULT_ENCODING = "utf-8"

PARAM_ARTIFICIAL_START_ACTIVITY = "pm4py:param:art_start_act"
PARAM_ARTIFICIAL_END_ACTIVITY = "pm4py:param:art_end_act"
DEFAULT_ARTIFICIAL_START_ACTIVITY = "▶"
DEFAULT_ARTIFICIAL_END_ACTIVITY = "■"

DEFAULT_BUSINESS_HOURS_WORKCALENDAR = None

SHOW_EVENT_LOG_DEPRECATION = True if get_param_from_env("PM4PY_SHOW_EVENT_LOG_DEPRECATION", "True").lower() == "true" else False
TRIGGERED_DT_PARSING_WARNING = False

DEFAULT_BGCOLOR = get_param_from_env("PM4PY_DEFAULT_BGCOLOR", "white")
DEFAULT_FORMAT_GVIZ_VIEW = get_param_from_env("PM4PY_DEFAULT_FORMAT_GVIZ_VIEW", "png")

ENABLE_MULTIPROCESSING_DEFAULT = True if get_param_from_env("PM4PY_ENABLE_MULTIPROCESSING_DEFAULT", "False").lower() == "true" else False
DEFAULT_READ_XES_LEGACY_OBJECT = True if get_param_from_env("PM4PY_DEFAULT_READ_XES_LEGACY_OBJECT", "False").lower() == "true" else False
DEFAULT_RETURN_DIAGNOSTICS_DATAFRAME = True if get_param_from_env("PM4PY_DEFAULT_RETURN_DIAGNOSTICS_DATAFRAME", "False").lower() == "true" else False

# Default business hour slots: Mondays to Fridays, 7:00 - 17:00 (in seconds)
DEFAULT_BUSINESS_HOUR_SLOTS = [
    ((0 * 24 + 7) * 60 * 60, (0 * 24 + 17) * 60 * 60),
    ((1 * 24 + 7) * 60 * 60, (1 * 24 + 17) * 60 * 60),
    ((2 * 24 + 7) * 60 * 60, (2 * 24 + 17) * 60 * 60),
    ((3 * 24 + 7) * 60 * 60, (3 * 24 + 17) * 60 * 60),
    ((4 * 24 + 7) * 60 * 60, (4 * 24 + 17) * 60 * 60),
]

OPENAI_MAX_LEN = int(get_param_from_env("PM4PY_OPENAI_MAX_LEN", "10000"))
OPENAI_API_KEY = get_param_from_env("PM4PY_OPENAI_API_KEY", None)
OPENAI_DEFAULT_MODEL = get_param_from_env("PM4PY_OPENAI_DEFAULT_MODEL", "gpt-3.5-turbo")
OPENAI_EXEC_RESULT = True if get_param_from_env("PM4PY_OPENAI_EXEC_RESULT", "False").lower() == "true" else False
DEFAULT_GVIZ_VIEW = get_param_from_env("PM4PY_DEFAULT_GVIZ_VIEW", None)

if pkgutil.find_loader("psutil"):
    import psutil

    parent_pid = os.getppid()
    parent_name = str(psutil.Process(parent_pid).name())

    if "PBIDesktop" in parent_name:
        DEFAULT_GVIZ_VIEW = "matplotlib_view"


if DEFAULT_GVIZ_VIEW is None:
    DEFAULT_GVIZ_VIEW = "view"


class AvailableSerializations(Enum):
    EVENT_LOG = "event_log"
    DATAFRAME = "dataframe"
    PETRI_NET = "petri_net"
    PROCESS_TREE = "process_tree"
    BPMN = "bpmn"
    DFG = "dfg"
